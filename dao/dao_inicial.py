from datetime import date
from conex.conn import Conex
from conex import config
from dao.base_dao import BaseDAO
from dao.seguridad import encriptarClave

USUARIO_DEFECTO = "admin"
CLAVE_DEFECTO = "Admin123*"

# Secuencia SQL que crea las tablas antes de que exista la vista
SECUENCIA_SQL = [
    """create table if not exists DEPARTAMENTO (
        IDDEPARTAMENTO int not null auto_increment,
        NOMBRE varchar(50) not null,
        IDGERENTE int null,
        primary key (IDDEPARTAMENTO),
        unique (NOMBRE) )""",

    """create table if not exists EMPLEADO (
        IDEMPLEADO int not null auto_increment,
        NOMBRE varchar(50) not null,
        APELLIDO varchar(50) not null,
        CORREO varchar(100) not null,
        FECHACONTRATO date not null,
        SALARIO int not null,
        DIRECCION varchar(100) not null,
        TELEFONO varchar(15) not null,
        IDDEPARTAMENTO int null,
        primary key (IDEMPLEADO),
        unique (CORREO),
        constraint FK_EMPLEADO_DEPARTAMENTO foreign key (IDDEPARTAMENTO)
            references DEPARTAMENTO (IDDEPARTAMENTO) on delete restrict on update restrict )""",

    """create table if not exists USUARIO (
        IDUSUARIO int not null auto_increment,
        NOMBREUSUARIO varchar(30) not null,
        CLAVE varchar(200) not null,
        ROL varchar(20) not null,
        IDEMPLEADO int not null,
        primary key (IDUSUARIO),
        unique (NOMBREUSUARIO),
        unique (IDEMPLEADO),
        constraint FK_USUARIO_EMPLEADO foreign key (IDEMPLEADO)
            references EMPLEADO (IDEMPLEADO) on delete restrict on update restrict )""",

    """create table if not exists PROYECTO (
        IDPROYECTO int not null auto_increment,
        NOMBRE varchar(80) not null,
        DESCRIPCION varchar(200) not null,
        FECHAINICIO date not null,
        primary key (IDPROYECTO),
        unique (NOMBRE) )""",

    """create table if not exists ASIGNACIONPROYECTO (
        IDASIGNACION int not null auto_increment,
        FECHAASIGNACION date not null,
        IDEMPLEADO int not null,
        IDPROYECTO int not null,
        primary key (IDASIGNACION),
        unique (IDEMPLEADO, IDPROYECTO),
        constraint FK_ASIGNACION_EMPLEADO foreign key (IDEMPLEADO)
            references EMPLEADO (IDEMPLEADO) on delete restrict on update restrict,
        constraint FK_ASIGNACION_PROYECTO foreign key (IDPROYECTO)
            references PROYECTO (IDPROYECTO) on delete restrict on update restrict )""",

    """create table if not exists REGISTROTIEMPO (
        IDREGISTRO int not null auto_increment,
        FECHA date not null,
        HORASTRABAJADAS int not null,
        DESCRIPCIONTAREA varchar(200) not null,
        IDEMPLEADO int not null,
        IDPROYECTO int not null,
        primary key (IDREGISTRO),
        constraint FK_REGISTRO_EMPLEADO foreign key (IDEMPLEADO)
            references EMPLEADO (IDEMPLEADO) on delete restrict on update restrict,
        constraint FK_REGISTRO_PROYECTO foreign key (IDPROYECTO)
            references PROYECTO (IDPROYECTO) on delete restrict on update restrict )""",
]

# La relación circular Departamento <-> Empleado (gerente) se agrega con ALTER una vez creadas ambas tablas
SQL_CONSULTA_FK_GERENTE = ("select count(*) as N from information_schema.TABLE_CONSTRAINTS "
                           "where CONSTRAINT_SCHEMA = %s and TABLE_NAME = 'DEPARTAMENTO' "
                           "and CONSTRAINT_NAME = 'FK_DEPARTAMENTO_GERENTE'")
SQL_FK_GERENTE = ("alter table DEPARTAMENTO add constraint FK_DEPARTAMENTO_GERENTE foreign key (IDGERENTE) "
                  "references EMPLEADO (IDEMPLEADO) on delete restrict on update restrict")


class InicializadorDAO(BaseDAO):
    """Usa el usuario por defecto de XAMPP (root) para crear la base de datos, las tablas
    y el usuario inicial del sistema ANTES de que la vista se ejecute."""

    # Constructor: sin base de datos seleccionada (aún puede no existir)
    def __init__(self) -> None:
        super().__init__(None)

    def crearEstructura(self) -> bool:
        c = Conex(config.HOST, config.USER, config.PASSWD, None)
        if not c.estaConectado():
            print("-No se pudo conectar a MySQL. Inicie los módulos Apache y MySQL en XAMPP-")
            print(f"-Detalle: {c.getError()}-")
            return False
        try:
            cursor = c.getConex().cursor()
            cursor.execute(f"create database if not exists {config.DATABASE} "
                           f"character set utf8mb4 collate utf8mb4_general_ci")
            cursor.execute(f"use {config.DATABASE}")
            for sql in SECUENCIA_SQL:
                cursor.execute(sql)

            cursor.execute(SQL_CONSULTA_FK_GERENTE, (config.DATABASE,))
            if cursor.fetchone()["N"] == 0:
                cursor.execute(SQL_FK_GERENTE)

            self.__crearUsuarioPorDefecto(cursor)
            c.getConex().commit()
            return True
        except Exception as ex:
            print(f"-No fue posible preparar la base de datos: {ex}-")
            try:
                c.getConex().rollback()
            except Exception:
                pass
            return False
        finally:
            c.closeConex()

    # Inserta el empleado y el usuario administrador solo si aún no existe ningún usuario
    def __crearUsuarioPorDefecto(self, cursor) -> None:
        cursor.execute("select count(*) as N from USUARIO")
        if cursor.fetchone()["N"] > 0:
            return
        cursor.execute("insert into EMPLEADO (NOMBRE, APELLIDO, CORREO, FECHACONTRATO, SALARIO, DIRECCION, TELEFONO, IDDEPARTAMENTO) "
                       "values (%s, %s, %s, %s, %s, %s, %s, %s)",
                       ("Administrador", "Sistema", "admin@ecotech.cl", date.today(), 0, "Sin dirección", "000000000", None))
        idEmpleado = cursor.lastrowid
        cursor.execute("insert into USUARIO (NOMBREUSUARIO, CLAVE, ROL, IDEMPLEADO) values (%s, %s, %s, %s)",
                       (USUARIO_DEFECTO, encriptarClave(CLAVE_DEFECTO), "ADMINISTRADOR", idEmpleado))
        print(f"-Usuario inicial creado -> usuario: {USUARIO_DEFECTO} | clave: {CLAVE_DEFECTO}-")
