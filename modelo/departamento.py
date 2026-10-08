from . import texto_opcional, texto_requerido


class Departamento:
    def __init__(self, nombre, descripcion="", id=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        self.__nombre = texto_requerido(valor, "El nombre del departamento", 2, 60)

    @property
    def descripcion(self):
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, valor):
        self.__descripcion = texto_opcional(valor, "La descripción", 200)

    def __str__(self):
        return f"[{self.id}] {self.nombre}"
