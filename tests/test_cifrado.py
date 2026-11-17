import os
import unittest
from datetime import date
from unittest.mock import patch
from cryptography.fernet import Fernet

os.environ["ECOTECH_CLAVE_CIFRADO"] = Fernet.generate_key().decode()   # clave solo para las pruebas

from controlador import sesion
from controlador.dto_empleado import EmpleadoDTO
from dao import cifrado
from dao.dao_empleado import EmpleadoDAO
from modelo.empleado import Empleado
from modelo.usuario import Usuario


def usuario(rol):
    return Usuario(1, "x", "", rol)


def nuevo():
    return Empleado(1, "Ana", "Paz", "ana@ecotech.cl", date(2026, 1, 1), 1200000, "Av. Solar 123", "912345678")


class TestCifrado(unittest.TestCase):
    def tearDown(self):
        sesion.cerrar()

    def test_ida_y_vuelta_y_no_deterministico(self):
        t1, t2 = cifrado.cifrar("hola"), cifrado.cifrar("hola")
        self.assertNotEqual(t1, t2)
        self.assertEqual(cifrado.descifrar(t1), "hola")
        self.assertTrue(cifrado.estaCifrado(t1))
        self.assertIsNone(cifrado.descifrar("gAAAA-basura"))

    def test_huella_correo_estable_e_insensible_a_mayusculas(self):
        self.assertEqual(cifrado.huellaCorreo("A@b.cl"), cifrado.huellaCorreo(" a@B.cl "))
        self.assertNotIn("a@b.cl", cifrado.huellaCorreo("a@b.cl"))

    def test_en_memoria_y_bd_solo_hay_cifrado(self):
        e = nuevo()
        for c in (e.getCorreoCifrado(), e.getSalarioCifrado(), e.getDireccionCifrada(), e.getTelefonoCifrado()):
            self.assertTrue(cifrado.estaCifrado(c))
        self.assertNotIn("ana@ecotech.cl", e.getCorreoCifrado())
        self.assertNotIn("912345678", e.getTelefonoCifrado())

    def test_visibilidad_por_rol(self):
        e = nuevo()
        for rol, ve in (("GERENTE_RRHH", True), ("ADMINISTRADOR", False), ("EMPLEADO", False), ("USUARIO", False)):
            sesion.iniciar(usuario(rol))
            if ve:
                self.assertEqual((e.getCorreo(), e.getSalario(), e.getDireccion(), e.getTelefono()),
                                 ("ana@ecotech.cl", 1200000, "Av. Solar 123", "912345678"))
                self.assertIn("ana@ecotech.cl", str(e))
                self.assertIn("912345678", str(e))
            else:
                self.assertEqual((e.getCorreo(), e.getSalario(), e.getDireccion(), e.getTelefono()),
                                 (cifrado.MASCARA,) * 4)
                texto = str(e)
                for secreto in ("ana@ecotech.cl", "1.200.000", "Av. Solar", "912345678"):
                    self.assertNotIn(secreto, texto)

    def test_sin_sesion_no_se_ve_nada(self):
        sesion.cerrar()
        self.assertEqual(nuevo().getSalario(), cifrado.MASCARA)
        self.assertEqual(nuevo().getTelefono(), cifrado.MASCARA)

    def test_setter_ignora_mascara(self):
        e = nuevo()
        antes = (e.getCorreoCifrado(), e.getSalarioCifrado(), e.getDireccionCifrada(), e.getTelefonoCifrado(),
                 e.getCorreoHash())
        e.setCorreo(cifrado.MASCARA); e.setSalario(cifrado.MASCARA); e.setDireccion(cifrado.MASCARA)
        e.setTelefono(cifrado.MASCARA)
        self.assertEqual(antes, (e.getCorreoCifrado(), e.getSalarioCifrado(), e.getDireccionCifrada(),
                                 e.getTelefonoCifrado(), e.getCorreoHash()))

    def test_clave_incorrecta_es_ilegible_no_cae(self):
        e = nuevo()
        e.setDatosCifrados(Fernet(Fernet.generate_key()).encrypt(b"x").decode(), "h", "", "", "")
        sesion.iniciar(usuario("GERENTE_RRHH"))
        self.assertEqual(e.getCorreo(), cifrado.ILEGIBLE)

    def test_admin_modifica_sin_ver_y_sin_borrar_datos(self):
        orig = nuevo()
        sesion.iniciar(usuario("ADMINISTRADOR"))
        with patch.object(EmpleadoDAO, "buscarEmpleado", return_value=orig), \
             patch.object(EmpleadoDAO, "_ejecutar", return_value=1) as ej:
            # el admin solo cambia el teléfono: el resto llega como "[ENCRIPTADO]" (ENTER para mantener)
            EmpleadoDTO().updateEmpleado(1, "Ana", "Paz", cifrado.MASCARA, date(2026, 1, 1), cifrado.MASCARA,
                                         cifrado.MASCARA, "955555555")
        params = ej.call_args[0][1]
        self.assertEqual(params[2:4], (orig.getCorreoCifrado(), orig.getCorreoHash()))
        self.assertEqual(params[5:7], (orig.getSalarioCifrado(), orig.getDireccionCifrada()))
        self.assertTrue(cifrado.estaCifrado(params[7]))
        self.assertNotIn("955555555", params[7])
        sesion.iniciar(usuario("GERENTE_RRHH"))
        self.assertEqual(orig.getCorreo(), "ana@ecotech.cl")
        self.assertEqual(orig.getTelefono(), "955555555")

    def test_admin_puede_cargar_un_correo_nuevo_sin_verlo(self):
        orig = nuevo()
        sesion.iniciar(usuario("ADMINISTRADOR"))
        with patch.object(EmpleadoDAO, "buscarEmpleado", return_value=orig), \
             patch.object(EmpleadoDAO, "_ejecutar", return_value=1):
            EmpleadoDTO().updateEmpleado(1, "Ana", "Paz", "nuevo@ecotech.cl", date(2026, 1, 1), 1300000,
                                         "Calle Nueva 5", "912345678")
        sesion.iniciar(usuario("GERENTE_RRHH"))
        self.assertEqual((orig.getCorreo(), orig.getSalario()), ("nuevo@ecotech.cl", 1300000))
        self.assertEqual(orig.getCorreoHash(), cifrado.huellaCorreo("nuevo@ecotech.cl"))

    def test_cifrar_pendientes_solo_toca_filas_en_claro(self):
        ya = cifrado.cifrar("b@b.cl")
        filas = [{"IDEMPLEADO": 1, "CORREO": "a@a.cl", "CORREOHASH": "x", "SALARIO": "99999",
                  "DIRECCION": "Recoleta", "TELEFONO": "911111111"},
                 {"IDEMPLEADO": 2, "CORREO": ya, "CORREOHASH": "h2", "SALARIO": cifrado.cifrar(5),
                  "DIRECCION": cifrado.cifrar("x"), "TELEFONO": cifrado.cifrar("922222222")}]
        with patch.object(EmpleadoDAO, "_consultar", return_value=filas), \
             patch.object(EmpleadoDAO, "_ejecutar", return_value=1) as ej:
            self.assertEqual(EmpleadoDAO().cifrarPendientes(), 1)
        c, h, sal, d, tel, idemp = ej.call_args[0][1]
        self.assertEqual((cifrado.descifrar(c), cifrado.descifrar(sal), cifrado.descifrar(d),
                          cifrado.descifrar(tel), idemp),
                         ("a@a.cl", "99999", "Recoleta", "911111111", 1))
        self.assertEqual(h, cifrado.huellaCorreo("a@a.cl"))
        self.assertEqual(ej.call_count, 1)

    def test_cifrar_pendientes_cifra_solo_el_telefono_de_una_bd_antigua(self):
        # base creada antes de cifrar el teléfono: correo, sueldo y dirección ya están cifrados
        correo, salario, direccion = cifrado.cifrar("c@c.cl"), cifrado.cifrar(7), cifrado.cifrar("Centro")
        filas = [{"IDEMPLEADO": 3, "CORREO": correo, "CORREOHASH": "h3", "SALARIO": salario,
                  "DIRECCION": direccion, "TELEFONO": "933333333"}]
        with patch.object(EmpleadoDAO, "_consultar", return_value=filas), \
             patch.object(EmpleadoDAO, "_ejecutar", return_value=1) as ej:
            self.assertEqual(EmpleadoDAO().cifrarPendientes(), 1)
        c, h, sal, d, tel, idemp = ej.call_args[0][1]
        self.assertEqual((c, h, sal, d, idemp), (correo, "h3", salario, direccion, 3))
        self.assertEqual(cifrado.descifrar(tel), "933333333")


if __name__ == "__main__":
    unittest.main()
