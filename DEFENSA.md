# Guía de defensa individual – ES2 TI3021

> ⚠ Ajusta nombres a **tu diagrama UML de la Unidad 1** si difiere (es lo primero que preguntarán).
> Cada integrante debe poder explicar TODO el proyecto, no solo su parte.

## Paso 1 · UML → Python (2.1.1)
| UML | Código |
|---|---|
| Clase `Empleado` (abstracta) | `modelo/empleado.py` → `class Empleado(ABC)` |
| Herencia (triángulo vacío) | `class Gerente(Empleado)` |
| Atributos privados `-rut` | `self.__rut` + `@property` |
| Asociación Departamento 1─* Empleado | `empleado.id_departamento` + FK en `empleado` |
| Asociación N:M Empleado–Proyecto | clase `AsignacionProyecto` + tabla `asignacion_proyecto` |
| Composición Asignación 1─* Registro | `registro_tiempo.id_asignacion` con `ON DELETE CASCADE` |

## Paso 2 · POO (2.1.2)
- **Encapsulamiento:** atributos `__privados` + setters que validan (`salario_base > 0`, RUT con dígito verificador…). Imposible crear un objeto inválido.
- **Abstracción/herencia/polimorfismo:** `calcular_salario()` abstracto; `costo_planilla()` suma sin `if tipo == ...`.
- **Sin duplicación:** `DAOBase` (obtener/listar/eliminar), `ControladorBase` (permisos), validadores reutilizables en `modelo/__init__.py` (los usa también la vista).
- **Patrón fábrica:** `crear_empleado(tipo, **datos)`. **Inyección de dependencias:** `main.construir_contexto`.

## Paso 3 · Base de datos (2.1.3)
- Librería oficial `sqlite3`. Parámetros: `row_factory=Row`, `PRAGMA foreign_keys=ON`, ruta por `ECOTECH_DB`.
- CRUD en `DAOBase` + DAOs: INSERT / SELECT / UPDATE / DELETE, siempre con `?`.
- `with self._con:` ⇒ commit si todo sale bien, rollback si falla.
- SQL avanzado: `JOIN`, `GROUP BY`, `SUM`, `LEFT JOIN` en reportes.

## Paso 4 · Errores y validaciones (2.1.4)
| Falla | Dónde se captura | Resultado |
|---|---|---|
| Archivo BD inaccesible | `Conexion.__init__` (`sqlite3.Error`, `OSError`) | `BaseDatosError`, la app informa y termina limpio |
| RUT/correo/usuario repetido | `IntegrityError` → `DuplicadoError` | mensaje claro |
| FK (borrar algo con datos asociados) | `IntegrityError` → `BaseDatosError` | rechazado |
| Dato mal digitado | `pedir_*` en `vista/validaciones.py` | repite la pregunta |
| Regla de negocio (exceder horas, proyecto cerrado) | controladores → `ValidacionError` | mensaje |
| Rol sin permiso | `_exigir()` → `PermisoError` | mensaje |
| Ctrl+C / fin de entrada | `seguro()` y `ejecutar()` | cancela la operación, no cierra |

## Paso 5 · Código de IA (2.1.5) — COMPLETA CON TU CASO REAL
Usa esta tabla con lo que **realmente** hiciste con la IA (la guía exige transparencia). Ejemplos típicos:

| Fragmento | Sugerencia de la IA | Problema | Decisión y criterio |
|---|---|---|---|
| Consultas SQL | f-strings con el dato incrustado | Inyección SQL (seguridad) | **Modificado** → parámetros `?` |
| Contraseñas | Guardar texto plano / MD5 | Reversible (seguridad) | **Descartado** → PBKDF2 + sal |
| `except:` | Captura genérica | Oculta fallas (estabilidad) | **Descartado** → excepciones específicas |
| Conexión | Abrir/cerrar por consulta | Ineficiente | **Modificado** → una `Conexion` reutilizada |
| Atributos | Públicos sin validar | Rompe encapsulamiento (coherencia con UML) | **Modificado** → propiedades |

Criterios para nombrar: **seguridad, eficiencia, coherencia con el diseño, mantenibilidad**.

## Preguntas típicas
1. ¿Por qué `DAOBase` es abstracta? → obliga a cada DAO a implementar `crear`, `actualizar`, `_mapear`.
2. ¿Por qué baja lógica? → conservar historial de horas/proyectos.
3. ¿Qué pasa si borro una asignación? → se borran sus horas (`CASCADE`); en cambio no puedo borrar un proyecto con asignaciones (`RESTRICT`).
4. ¿Cómo evitas la inyección SQL? → parámetros `?`; hay un test (`test_inyeccion_sql_se_trata_como_texto`).
