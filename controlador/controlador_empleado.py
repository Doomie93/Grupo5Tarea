from dao.excepciones import ValidacionError
from modelo.empleado import crear_empleado
from modelo.usuario import ADMIN, GERENTE

from .controlador_base import ControladorBase

_EDITABLES = {"rut", "nombre", "email", "salario_base", "fecha_ingreso", "id_departamento"}


class ControladorEmpleado(ControladorBase):
    def __init__(self, sesion, dao_empleado, dao_departamento):
        super().__init__(sesion)
        self._dao = dao_empleado
        self._dao_depto = dao_departamento

    def registrar(self, tipo, rut, nombre, email, salario_base, fecha_ingreso=None, id_departamento=None):
        self._exigir(ADMIN, GERENTE)
        if id_departamento is not None:
            self._dao_depto.obtener(id_departamento)  # valida que exista
        e = crear_empleado(tipo, rut=rut, nombre=nombre, email=email, salario_base=salario_base,
                           fecha_ingreso=fecha_ingreso, id_departamento=id_departamento)
        return self._dao.crear(e)

    def listar(self, solo_activos=True):
        self._exigir(ADMIN, GERENTE)
        return self._dao.listar_activos() if solo_activos else self._dao.listar()

    def obtener(self, id_empleado):
        self._exigir(ADMIN, GERENTE)
        return self._dao.obtener(id_empleado)

    def buscar(self, texto):
        self._exigir(ADMIN, GERENTE)
        if len((texto or "").strip()) < 2:
            raise ValidacionError("Ingrese al menos 2 caracteres para buscar.")
        return self._dao.buscar(texto)

    def actualizar(self, id_empleado, **campos):
        self._exigir(ADMIN, GERENTE)
        invalidos = set(campos) - _EDITABLES
        if invalidos:
            raise ValidacionError(f"Campos no editables: {', '.join(sorted(invalidos))}")
        e = self._dao.obtener(id_empleado)
        if campos.get("id_departamento") is not None:
            self._dao_depto.obtener(campos["id_departamento"])
        for campo, valor in campos.items():
            setattr(e, campo, valor)  # cada setter valida
        self._dao.actualizar(e)
        return e

    def dar_de_baja(self, id_empleado):
        """Baja lógica: conserva el historial de proyectos y horas."""
        self._exigir(ADMIN, GERENTE)
        e = self._dao.obtener(id_empleado)
        e.activo = False
        self._dao.actualizar(e)

    def reactivar(self, id_empleado):
        self._exigir(ADMIN, GERENTE)
        e = self._dao.obtener(id_empleado)
        e.activo = True
        self._dao.actualizar(e)

    def eliminar(self, id_empleado):
        self._exigir(ADMIN)
        self._dao.eliminar(id_empleado)

    def costo_planilla(self):
        """Suma polimórfica de la remuneración de los empleados activos."""
        return sum(e.calcular_salario() for e in self.listar(True))
