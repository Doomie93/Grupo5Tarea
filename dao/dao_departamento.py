from dao.base_dao import BaseDAO
from modelo.departamento import Departamento
from modelo.empleado import Empleado


class DepartamentoDAO(BaseDAO):

    # Trae todas las filas de DEPARTAMENTO (el DTO las convierte en objetos)
    def cargarDatos(self) -> list:
        return self._consultar("select IDDEPARTAMENTO, NOMBRE, IDGERENTE from DEPARTAMENTO order by IDDEPARTAMENTO")

    # Agrega un departamento a la BD y a la lista de clase
    def registrarDepto(self, depto: Departamento) -> int:
        gerente = depto.getGerente()
        res = self._ejecutar("insert into DEPARTAMENTO (NOMBRE, IDGERENTE) values (%s, %s)",
                             (depto.getNombre(), gerente.getId() if gerente is not None else None))
        if res > 0:
            depto.setId(self.getUltimoId())
            Departamento().getListaDepartamentos().append(depto)
        return res

    # Retorna la lista de clase
    def mostrarDeptos(self) -> list:
        return Departamento().getListaDepartamentos()

    # Busca un departamento en la lista de clase
    def buscarDepto(self, idDepto: int) -> Departamento:
        for depto in Departamento().getListaDepartamentos():
            if depto.getId() == idDepto:
                return depto
        return None

    # Modifica en la BD y actualiza el objeto de la lista (se mantiene la misma referencia)
    def modificarDepto(self, depto: Departamento) -> int:
        gerente = depto.getGerente()
        res = self._ejecutar("update DEPARTAMENTO set NOMBRE = %s, IDGERENTE = %s where IDDEPARTAMENTO = %s",
                             (depto.getNombre(), gerente.getId() if gerente is not None else None, depto.getId()))
        if res > 0:
            actual = self.buscarDepto(depto.getId())
            if actual is not None:
                actual.setNombre(depto.getNombre())
                actual.setGerente(gerente)
        return res

    # Elimina de la BD y de la lista de clase
    def eliminarDepto(self, idDepto: int) -> int:
        res = self._ejecutar("delete from DEPARTAMENTO where IDDEPARTAMENTO = %s", (idDepto,))
        if res > 0:
            lista = Departamento().getListaDepartamentos()
            lista[:] = [d for d in lista if d.getId() != idDepto]
        return res

    # Asigna un departamento a un empleado que aún no pertenece a ninguno
    def agregarEmpleadoDepto(self, empleado: Empleado, depto: Departamento) -> int:
        res = self._ejecutar("update EMPLEADO set IDDEPARTAMENTO = %s where IDEMPLEADO = %s",
                             (depto.getId(), empleado.getId()))
        if res > 0:
            empleado.setDepartamento(depto)
            if empleado not in depto.getEmpleados():
                depto.getEmpleados().append(empleado)
        return res

    # Mueve un empleado desde su departamento actual a otro
    def reasignarEmpleadoDepto(self, empleado: Empleado, depto: Departamento) -> int:
        anterior = empleado.getDepartamento()
        res = self._ejecutar("update EMPLEADO set IDDEPARTAMENTO = %s where IDEMPLEADO = %s",
                             (depto.getId(), empleado.getId()))
        if res > 0:
            if anterior is not None and empleado in anterior.getEmpleados():
                anterior.getEmpleados().remove(empleado)
            empleado.setDepartamento(depto)
            if empleado not in depto.getEmpleados():
                depto.getEmpleados().append(empleado)
        return res
