from dao.base_dao import BaseDAO
from modelo.empleado import Empleado
from dao import cifrado


class EmpleadoDAO(BaseDAO):

    # Trae todas las filas de EMPLEADO (el DTO las convierte en objetos)
    def cargarDatos(self) -> list:
        return self._consultar("select IDEMPLEADO, NOMBRE, APELLIDO, CORREO, CORREOHASH, FECHACONTRATO, SALARIO, "
                               "DIRECCION, TELEFONO, IDDEPARTAMENTO from EMPLEADO order by IDEMPLEADO")

    # Cifra los datos que aún estén en claro en la BD (por ejemplo los empleados creados con el script SQL).
    # Es seguro ejecutarlo varias veces: la app siempre guarda las tres columnas cifradas, así que una fila con el
    # correo en claro es una fila pendiente. Retorna cuántas filas cifró.
    def cifrarPendientes(self) -> int:
        filas = self._consultar("select IDEMPLEADO, CORREO, SALARIO, DIRECCION from EMPLEADO") or []
        total = 0
        for f in filas:
            if cifrado.estaCifrado(str(f["CORREO"])):
                continue
            res = self._ejecutar(
                "update EMPLEADO set CORREO = %s, CORREOHASH = %s, SALARIO = %s, DIRECCION = %s where IDEMPLEADO = %s",
                (cifrado.cifrar(f["CORREO"]), cifrado.huellaCorreo(f["CORREO"]), cifrado.cifrar(f["SALARIO"]),
                 cifrado.cifrar(f["DIRECCION"]), f["IDEMPLEADO"]))
            total += 1 if res > 0 else 0
        return total

    # Agrega un empleado a la BD, a la lista de clase y a la lista de su departamento
    def registrarEmpleado(self, empleado: Empleado) -> int:
        depto = empleado.getDepartamento()
        sql = ("insert into EMPLEADO (NOMBRE, APELLIDO, CORREO, CORREOHASH, FECHACONTRATO, SALARIO, DIRECCION, TELEFONO, "
               "IDDEPARTAMENTO) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
        res = self._ejecutar(sql, (empleado.getNombre(), empleado.getApellido(), empleado.getCorreoCifrado(),
                                   empleado.getCorreoHash(), empleado.getFechaContrato(),
                                   empleado.getSalarioCifrado(), empleado.getDireccionCifrada(),
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
        sql = ("update EMPLEADO set NOMBRE = %s, APELLIDO = %s, CORREO = %s, CORREOHASH = %s, FECHACONTRATO = %s, "
               "SALARIO = %s, DIRECCION = %s, TELEFONO = %s where IDEMPLEADO = %s")
        res = self._ejecutar(sql, (empleado.getNombre(), empleado.getApellido(), empleado.getCorreoCifrado(),
                                   empleado.getCorreoHash(), empleado.getFechaContrato(),
                                   empleado.getSalarioCifrado(), empleado.getDireccionCifrada(),
                                   empleado.getTelefono(), empleado.getId()))
        if res > 0:
            actual = self.buscarEmpleado(empleado.getId())
            if actual is not None:
                actual.setNombre(empleado.getNombre())
                actual.setApellido(empleado.getApellido())
                actual.setFechaContrato(empleado.getFechaContrato())
                actual.copiarDatosCifrados(empleado)
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
