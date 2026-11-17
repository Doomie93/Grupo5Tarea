import unittest
from datetime import date
from unittest.mock import patch, MagicMock
import requests

from servicios import api_indicadores as ind, api_clima as clima
from servicios.http_seguro import ErrorServicio
from controlador.dto_indicador import IndicadorDTO
from modelo.usuario import Usuario


def resp(status=200, json=None, texto=None):
    r = MagicMock()
    r.status_code = status
    r.content = b"x"
    if texto is not None:
        r.json.side_effect = ValueError("no json")
    else:
        r.json.return_value = json
    return r


def serie(*pares, autor="x"):
    return {"autor": autor, "serie": [{"fecha": f, "valor": v} for f, v in pares]}


class TestIndicadores(unittest.TestCase):
    @patch("requests.get")
    def test_findic_ok(self, g):
        g.return_value = resp(json=serie(("2026-01-15", 900.5)))
        r = ind.obtenerPorFecha("dolar", date(2026, 1, 15))
        self.assertEqual(r, [{"autor": "findic.cl", "fecha": date(2026, 1, 15), "valor": 900.5}])
        self.assertIn("https://findic.cl/api/dolar/15-01-2026", g.call_args[0][0])

    @patch("requests.get")
    def test_fallback_mindicador_si_findic_500(self, g):
        g.side_effect = [resp(500, {}), resp(json=serie(("2026-01-15T03:00:00.000Z", 901.0)))]
        r = ind.obtenerPorFecha("dolar", date(2026, 1, 15))
        self.assertEqual(r[0]["autor"], "mindicador.cl")
        self.assertEqual(r[0]["fecha"], date(2026, 1, 15))

    @patch("requests.get")
    def test_fallback_en_timeout_conexion_y_json_invalido(self, g):
        for fallo in (requests.exceptions.Timeout(), requests.exceptions.ConnectionError("secreto"), resp(200, texto="<html>")):
            g.side_effect = [fallo, resp(json=serie(("2026-01-15", 1.0)))]
            self.assertEqual(ind.obtenerPorFecha("uf", date(2026, 1, 15))[0]["autor"], "mindicador.cl")

    @patch("requests.get")
    def test_todas_fallan_mensaje_seguro(self, g):
        g.side_effect = requests.exceptions.ConnectionError("HTTPSConnectionPool(host='findic.cl') secreto")
        with self.assertRaises(ErrorServicio) as cm:
            ind.obtenerUltimo("uf")
        self.assertNotIn("findic", str(cm.exception))
        self.assertNotIn("secreto", str(cm.exception))

    @patch("requests.get")
    def test_codigos_http(self, g):
        for codigo in (404, 429, 500, 503, 418):
            g.side_effect = None
            g.return_value = resp(codigo, {})
            with self.assertRaises(ErrorServicio):
                ind.obtenerUltimo("uf")

    @patch("requests.get")
    def test_estructura_invalida_y_items_malos(self, g):
        g.return_value = resp(json={"sin": "serie"})
        with self.assertRaises(ErrorServicio):
            ind.obtenerUltimo("uf")
        g.return_value = resp(json={"serie": [{"fecha": "mala", "valor": 1}, {"fecha": "2026-01-01", "valor": "abc"},
                                              {"fecha": "2026-01-02", "valor": 5}]})
        self.assertEqual(len(ind.obtenerUltimo("uf")), 1)

    def test_codigo_no_permitido(self):
        with self.assertRaises(ErrorServicio):
            ind.obtenerUltimo("../admin")

    @patch("requests.get")
    def test_ultimo_toma_la_fecha_mayor(self, g):
        g.return_value = resp(json=serie(("2026-01-14", 1), ("2026-01-16", 3), ("2026-01-15", 2)))
        self.assertEqual(ind.obtenerUltimo("uf")[0]["valor"], 3)

    @patch("requests.get")
    def test_rango_varios_anios_filtra_y_ordena(self, g):
        g.side_effect = [resp(json=serie(("2025-12-31", 3), ("2025-12-01", 1), ("2025-06-01", 0))),
                         resp(json=serie(("2026-01-02", 4), ("2026-02-01", 9)))]
        r = ind.obtenerRango("uf", date(2025, 12, 1), date(2026, 1, 31))
        self.assertEqual([x["valor"] for x in r], [1, 3, 4])
        self.assertEqual(g.call_count, 2)

    def test_rango_invalido(self):
        with self.assertRaises(ErrorServicio):
            ind.obtenerRango("uf", date(2026, 2, 1), date(2026, 1, 1))
        with self.assertRaises(ErrorServicio):
            ind.obtenerRango("uf", date(2018, 1, 1), date(2026, 1, 1))

    @patch("requests.get")
    def test_utm_usa_dia_1(self, g):
        g.return_value = resp(json=serie(("2026-01-01", 69000)))
        r = ind.obtenerPorFecha("utm", date(2026, 1, 15))
        self.assertIn("01-01-2026", g.call_args[0][0])
        self.assertEqual(r[0]["valor"], 69000)


class TestClima(unittest.TestCase):
    GEO = {"results": [{"name": "Calama", "admin1": "Antofagasta", "country": "Chile",
                        "latitude": -22.4, "longitude": -68.9}]}

    def fc(self, mj=25.0, rafagas=20, lluvia=5, uv=9.0):
        return {"current": {"temperature_2m": 25.1, "relative_humidity_2m": 40, "precipitation": 0, "weather_code": 1,
                            "wind_speed_10m": 10, "cloud_cover": 10, "shortwave_radiation": 800},
                "daily": {"time": ["2026-11-16"], "weather_code": [1], "temperature_2m_max": [28], "temperature_2m_min": [12],
                          "precipitation_probability_max": [lluvia], "shortwave_radiation_sum": [mj],
                          "sunshine_duration": [43200], "uv_index_max": [uv], "wind_gusts_10m_max": [rafagas]}}

    def test_validaciones(self):
        for ok in ("Santiago", "Punta Arenas", "Valparaíso", "O'Higgins", "Viña-del-Mar"):
            self.assertTrue(clima.validarCiudad(ok), ok)
        for mal in ("", "a", "Santiago; DROP", "123", "../x", "a" * 61, "Lima?x=1&"):
            self.assertFalse(clima.validarCiudad(mal), mal)
        self.assertTrue(clima.validarPais("cl"))
        self.assertFalse(clima.validarPais("CHL"))

    @patch("requests.get")
    def test_clima_solar(self, g):
        g.side_effect = [resp(json=self.GEO), resp(json=self.fc(mj=25.0))]      # 25 MJ/m² = 6.9 kWh/m²
        c = clima.obtenerClima("Calama", "CL")
        d = c["pronostico"][0]
        self.assertAlmostEqual(d["energia"], 25 / 3.6)
        self.assertEqual(d["sol"], 12)
        txt = " ".join(clima.evaluarProyecto(c))
        self.assertIn("potencial solar ALTO", txt)
        self.assertIn("UV 9", txt)

    def test_potencial_y_terreno(self):
        self.assertEqual([clima.potencialSolar(x) for x in (6, 4, 1)], ["ALTO", "MEDIO", "BAJO"])
        dia = {"rafagas": 70, "lluvia": 80, "uv": 3}
        self.assertEqual(len(clima.aptoParaTrabajoEnTerreno(dia)), 2)
        self.assertEqual(clima.aptoParaTrabajoEnTerreno({"rafagas": 10, "lluvia": None, "uv": 2}), [])

    @patch("requests.get")
    def test_bajo_potencial_advierte(self, g):
        g.side_effect = [resp(json=self.GEO), resp(json=self.fc(mj=4.0))]
        self.assertIn("bajo potencial", " ".join(clima.evaluarProyecto(clima.obtenerClima("Calama"))))

    @patch("requests.get")
    def test_ciudad_inexistente_y_datos_invalidos(self, g):
        g.return_value = resp(json={"generationtime_ms": 1})
        with self.assertRaises(ErrorServicio):
            clima.obtenerClima("Zzzzz")
        bad = self.fc()
        bad["current"]["cloud_cover"] = 500
        g.side_effect = [resp(json=self.GEO), resp(json=bad)]
        with self.assertRaises(ErrorServicio):
            clima.obtenerClima("Calama")

    def test_entrada_invalida_no_llama_api(self):
        with patch("requests.get") as g:
            with self.assertRaises(ErrorServicio):
                clima.obtenerClima("<script>")
            g.assert_not_called()


class TestPermisos(unittest.TestCase):
    def test_solo_gerente_rrhh(self):
        for rol, permitido in (("GERENTE_RRHH", True), ("ADMINISTRADOR", False), ("EMPLEADO", False), ("USUARIO", False)):
            u = Usuario(1, "x", "", rol)
            with patch("requests.get") as g:
                g.return_value = resp(json=serie(("2026-01-15", 1.0)))
                if permitido:
                    self.assertEqual(len(IndicadorDTO().consultar(u, "uf")), 1)
                else:
                    with self.assertRaises(ErrorServicio):
                        IndicadorDTO().consultar(u, "uf")
                    g.assert_not_called()

    def test_sin_usuario(self):
        with self.assertRaises(ErrorServicio):
            IndicadorDTO().consultar(None, "uf")

    def test_guardar_usa_id_de_usuario_y_autor(self):
        u = Usuario(7, "g", "", "GERENTE_RRHH")
        with patch("requests.get") as g, patch("dao.dao_indicador.IndicadorDAO._ejecutarVarios", return_value=1) as ej:
            g.return_value = resp(json=serie(("2026-01-15", 1.5)))
            lista = IndicadorDTO().consultar(u, "dolar")
            msg = IndicadorDTO().guardar(lista)
        self.assertIn("almacenado", msg)
        self.assertEqual(ej.call_args[0][1], [(7, "findic.cl", "dolar", date(2026, 1, 15), 1.5)])


if __name__ == "__main__":
    unittest.main()
