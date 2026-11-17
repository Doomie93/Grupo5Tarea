from controlador.base_dto import BaseDTO
from controlador.permisos import puedeUsarServiciosExternos
from dao.dao_indicador import IndicadorDAO
from modelo.indicador import Indicador
from servicios import api_indicadores, api_clima
from servicios.http_seguro import ErrorServicio


class IndicadorDTO(BaseDTO):

    # Segunda barrera de seguridad: aunque la vista falle en ocultar el menú, el servicio no se ejecuta sin el rol
    def _exigirPermiso(self, usuario) -> None:
        if not puedeUsarServiciosExternos(usuario):
            raise ErrorServicio("Acceso denegado: solo el Gerente de Recursos Humanos puede usar servicios externos.")

    # Consulta la API (fecha=None -> último valor; fecha -> día puntual; desde/hasta -> rango).
    # Retorna lista de Indicador (aún sin guardar). Lanza ErrorServicio con mensaje seguro si falla.
    def consultar(self, usuario, codigo: str, fecha=None, desde=None, hasta=None) -> list:
        self._exigirPermiso(usuario)
        if desde is not None and hasta is not None:
            datos = api_indicadores.obtenerRango(codigo, desde, hasta)
        elif fecha is not None:
            datos = api_indicadores.obtenerPorFecha(codigo, fecha)
        else:
            datos = api_indicadores.obtenerUltimo(codigo)
        return [Indicador(0, usuario.getId(), d["autor"], codigo, d["fecha"], d["valor"]) for d in datos]

    def guardar(self, lista: list) -> str:
        if len(lista) == 0:
            return "No hay datos para guardar."
        return self.mensaje(IndicadorDAO().registrarIndicadores(lista),
                            f"{len(lista)} valor(es) almacenado(s) en la base de datos.")

    def historial(self, usuario, codigo: str = None, limite: int = 30) -> list:
        self._exigirPermiso(usuario)
        return IndicadorDAO().listarIndicadores(codigo, limite)

    def clima(self, usuario, ciudad: str, pais: str = "") -> tuple:
        self._exigirPermiso(usuario)
        datos = api_clima.obtenerClima(ciudad, pais)
        return datos, api_clima.evaluarProyecto(datos)
