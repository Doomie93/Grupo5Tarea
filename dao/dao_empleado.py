from dao.base_dao import BaseDAO
from modelo.empleado import Empleado


class EmpleadoDAO(BaseDAO):

    # Trae todas las filas de EMPLEADO (el DTO las convierte en objetos)
    def cargarDatos(self) -> list:
        return self._consultar("select IDEMPLEADO, NOMBRE, APELLIDO, CORREO, FECHACONTRATO, SALARIO, "
                               "DIRECCION, TELEFONO, IDDEPARTAMENTO from EMPLEADO order by IDEMPLEADO")

    # Agrega un empleado a la BD, a la lista de clase y a la lista de su departamento
    def registrarEmpleado(self, empleado: Empleado) -> int:
        depto = empleado.getDepartamento()
        sql = ("insert into EMPLEADO (NOMBRE, APELLIDO, CORREO, FECHACONTRATO, SALARIO, DIRECCION, TELEFONO, IDDEPARTAMENTO) "
               "values (%s, %s, %s, %s, %s, %s, %s, %s)")
        res = self._ejecutar(sql, (empleado.getNombre(), empleado.getApellido(), empleado.getCorreo(),
                                   empleado.getFechaContrato(), empleado.getSalario(), empleado.getDireccion(),
                                   empleado.getTelefono(), depto.getId() if depto is not None else None))
        if res > 0:
            empleado.setId(self.getUltimoId())
            Empleado().getListaEmpleados().append(empleado)
            if depto is not None:
                depto.getEmpleados().append(empleado)
        return res

    # Retorna la lista de clase
    def mostrarEmpleados(self) -> list:
        return Empleado().getListaEmpleados()

    # Busca un empleado en la lista de clase
    def buscarEmpleado(self, idEmpleado: int) -> Empleado:
        for emp in Empleado().getListaEmpleados():
            if emp.getId() == idEmpleado:
                return emp
        return None

    # Modifica en la BD y actualiza el objeto de la lista (el departamento se cambia desde DepartamentoDAO)
    def modificarEmpleado(self, empleado: Empleado) -> int:
        sql = ("update EMPLEADO set NOMBRE = %s, APELLIDO = %s, CORREO = %s, FECHACONTRATO = %s, SALARIO = %s, "
               "DIRECCION = %s, TELEFONO = %s where IDEMPLEADO = %s")
        res = self._ejecutar(sql, (empleado.getNombre(), empleado.getApellido(), empleado.getCorreo(),
                                   empleado.getFechaContrato(), empleado.getSalario(), empleado.getDireccion(),
                                   empleado.getTelefono(), empleado.getId()))
        if res > 0:
            actual = self.buscarEmpleado(empleado.getId())
            if actual is not None:
                actual.setNombre(empleado.getNombre())
                actual.setApellido(empleado.getApellido())
                actual.setCorreo(empleado.getCorreo())
                actual.setFechaContrato(empleado.getFechaContrato())
                actual.setSalario(empleado.getSalario())
                actual.setDireccion(empleado.getDireccion())
                actual.setTelefono(empleado.getTelefono())
        return res

    # Elimina de la BD, de la lista de clase y de la lista de su departamento
    def eliminarEmpleado(self, idEmpleado: int) -> int:
        actual = self.buscarEmpleado(idEmpleado)
        res = self._ejecutar("delete from EMPLEADO where IDEMPLEADO = %s", (idEmpleado,))
        if res > 0:
            lista = Empleado().getListaEmpleados()
            lista[:] = [e for e in lista if e.getId() != idEmpleado]
            if actual is not None and actual.getDepartamento() is not None:
                deptoEmpleados = actual.getDepartamento().getEmpleados()
                deptoEmpleados[:] = [e for e in deptoEmpleados if e.getId() != idEmpleado]
        return res
