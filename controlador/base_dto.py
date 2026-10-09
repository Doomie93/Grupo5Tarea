from dao.base_dao import ERROR_DUPLICADO, ERROR_RELACION, ERROR_CONEXION


class BaseDTO():
    """Convierte el código numérico que entrega el DAO en un mensaje para la vista."""

    def mensaje(self, resultado: int, exito: str) -> str:
        if resultado > 0:
            return exito
        if resultado == 0:
            return "No se realizaron cambios."
        if resultado == ERROR_DUPLICADO:
            return "Ya existe un registro con esos datos (valor duplicado)."
        if resultado == ERROR_RELACION:
            return "Operación no permitida: existen datos relacionados."
        if resultado == ERROR_CONEXION:
            return "No hay conexión con la base de datos. Verifique que MySQL esté activo en XAMPP."
        return "Problemas con la base de datos..vuelva a intentarlo."
