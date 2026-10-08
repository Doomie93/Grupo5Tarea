-- =====================================================================
-- EcoTech Solutions - Sistema de Gestión (SQLite)
-- Idempotente: se puede ejecutar varias veces sin perder datos.
-- =====================================================================
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS departamento (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL UNIQUE,
    descripcion TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS empleado (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo            TEXT NOT NULL CHECK (tipo IN ('PLANTA','HONORARIOS','GERENTE')),
    rut             TEXT NOT NULL UNIQUE,
    nombre          TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    salario_base    REAL NOT NULL CHECK (salario_base > 0),
    fecha_ingreso   TEXT NOT NULL,
    id_departamento INTEGER REFERENCES departamento(id) ON DELETE RESTRICT,
    activo          INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE IF NOT EXISTS usuario (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol           TEXT NOT NULL CHECK (rol IN ('ADMIN','GERENTE','EMPLEADO')),
    id_empleado   INTEGER REFERENCES empleado(id) ON DELETE SET NULL,
    activo        INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);

CREATE TABLE IF NOT EXISTS proyecto (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL UNIQUE,
    descripcion  TEXT NOT NULL DEFAULT '',
    fecha_inicio TEXT NOT NULL,
    fecha_fin    TEXT,
    estado       TEXT NOT NULL DEFAULT 'PLANIFICADO'
                 CHECK (estado IN ('PLANIFICADO','EN_CURSO','FINALIZADO','CANCELADO')),
    presupuesto  REAL NOT NULL DEFAULT 0 CHECK (presupuesto >= 0)
);

CREATE TABLE IF NOT EXISTS asignacion_proyecto (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    id_empleado      INTEGER NOT NULL REFERENCES empleado(id) ON DELETE RESTRICT,
    id_proyecto      INTEGER NOT NULL REFERENCES proyecto(id) ON DELETE RESTRICT,
    rol_proyecto     TEXT NOT NULL,
    horas_asignadas  REAL NOT NULL CHECK (horas_asignadas > 0),
    fecha_asignacion TEXT NOT NULL,
    UNIQUE (id_empleado, id_proyecto)
);

CREATE TABLE IF NOT EXISTS registro_tiempo (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    id_asignacion INTEGER NOT NULL REFERENCES asignacion_proyecto(id) ON DELETE CASCADE,
    fecha         TEXT NOT NULL,
    horas         REAL NOT NULL CHECK (horas > 0 AND horas <= 24),
    descripcion   TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_empleado_depto  ON empleado(id_departamento);
CREATE INDEX IF NOT EXISTS idx_asig_empleado   ON asignacion_proyecto(id_empleado);
CREATE INDEX IF NOT EXISTS idx_asig_proyecto   ON asignacion_proyecto(id_proyecto);
CREATE INDEX IF NOT EXISTS idx_registro_asig   ON registro_tiempo(id_asignacion);

-- Datos iniciales (sin credenciales: el primer administrador se crea al iniciar la app)
INSERT OR IGNORE INTO departamento (nombre, descripcion) VALUES
    ('Tecnología',       'Desarrollo y soporte de sistemas'),
    ('Recursos Humanos', 'Gestión de personas'),
    ('Operaciones',      'Operación de plantas y proyectos'),
    ('Finanzas',         'Contabilidad y presupuestos');
