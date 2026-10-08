# EcoTech Solutions · Sistema de Gestión (ES2 – TI3021)

Aplicación de consola en Python (POO + SQLite) para gestionar empleados, departamentos,
proyectos, asignaciones y registro de horas, con autenticación por roles.

## Ejecutar
```bash
python main.py                      # requiere Python 3.9+, sin dependencias externas
python -m pruebas.verificar_bd      # comprueba conexión y tablas
python -m unittest discover -s pruebas -t .   # 34 pruebas automáticas
```
La BD se crea sola en `base_datos/ecotech_gestion.db` (o en la ruta de la variable `ECOTECH_DB`).
En el primer uso el sistema pide crear el administrador (no hay credenciales por defecto).

## Arquitectura en capas
```
eco_tech_ES2/
├── base_datos/ecotech_gestion.sql   Esquema + datos iniciales (idempotente)
├── conex/conexion.py                Única clase que usa sqlite3; traduce errores a excepciones propias
├── modelo/                          Entidades con encapsulamiento y validación (sin acceso a BD)
│   ├── empleado.py                  Empleado (abstracta) ◁ EmpleadoPlanta · EmpleadoHonorarios · Gerente
│   ├── departamento.py · proyecto.py · asignacion_proyecto.py · registro_tiempo.py · usuario.py
├── dao/                             Acceso a datos: SQL parametrizado, un DAO por entidad
│   ├── dao_base.py                  Clase abstracta con lo común (obtener/listar/eliminar/contar)
│   ├── dao_*.py · excepciones.py    Jerarquía EcoTechError → Validacion/BaseDatos/Duplicado/…
├── controlador/                     Reglas de negocio + permisos por rol (RBAC)
├── vista/                           Menús de consola y entrada validada con reintento
├── pruebas/                         Tests unitarios y verificación de BD
└── main.py                          Ensamblado de dependencias y arranque
```
Flujo: `vista → controlador → dao → conex → SQLite`. Cada capa solo conoce a la siguiente.

## Modelo de datos
`departamento 1─* empleado` · `empleado *─* proyecto` (vía `asignacion_proyecto`) ·
`asignacion_proyecto 1─* registro_tiempo` · `usuario *─0..1 empleado`

## Roles
| Rol | Puede |
|---|---|
| ADMIN | Todo, incluida gestión de usuarios y eliminaciones definitivas |
| GERENTE | Empleados, departamentos, proyectos, asignaciones, horas y reportes |
| EMPLEADO | Ver sus asignaciones y registrar/ver **solo sus** horas |

## Seguridad aplicada
- Contraseñas con PBKDF2-HMAC-SHA256, sal aleatoria y comparación en tiempo constante.
- Bloqueo de 60 s tras 3 intentos fallidos; mensaje de error genérico (no revela si el usuario existe).
- Consultas 100 % parametrizadas (sin inyección SQL); `PRAGMA foreign_keys=ON`; restricciones `CHECK`/`UNIQUE` en la BD.
- Validación en dos niveles: entrada (vista) y dominio (setters del modelo).
- Baja lógica de empleados para conservar historial; no se puede dejar el sistema sin administrador.
