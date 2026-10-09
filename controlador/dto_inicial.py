from dao.dao_inicial import InicializadorDAO


class InicializadorDTO():

    # Crea la BD, las tablas y el usuario inicial usando el usuario por defecto de XAMPP
    def prepararBaseDatos(self) -> bool:
        return InicializadorDAO().crearEstructura()
