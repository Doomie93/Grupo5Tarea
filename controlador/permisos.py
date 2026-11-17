# Roles del sistema y qué puede hacer cada uno
ADMINISTRADOR = "ADMINISTRADOR"
GERENTE_RRHH = "GERENTE_RRHH"
EMPLEADO = "EMPLEADO"

ROLES = [ADMINISTRADOR, GERENTE_RRHH, EMPLEADO]

# Los usuarios antiguos con rol "USUARIO" se tratan como EMPLEADO (mínimo privilegio)
def rolEfectivo(rol: str) -> str:
    return rol if rol in (ADMINISTRADOR, GERENTE_RRHH) else EMPLEADO


def esAdministrador(usuario) -> bool:
    return usuario is not None and rolEfectivo(usuario.getRol()) == ADMINISTRADOR


def esGerenteRRHH(usuario) -> bool:
    return usuario is not None and rolEfectivo(usuario.getRol()) == GERENTE_RRHH


# Solo el Gerente de Recursos Humanos puede consumir las APIs externas (indicadores y clima)
def puedeUsarServiciosExternos(usuario) -> bool:
    return esGerenteRRHH(usuario)


# Solo el Gerente de Recursos Humanos puede ver correo, sueldo, dirección y teléfono de los empleados.
# Para el resto de los roles (incluido el administrador) esos datos se muestran encriptados.
def puedeVerDatosSensibles(usuario) -> bool:
    return esGerenteRRHH(usuario)
