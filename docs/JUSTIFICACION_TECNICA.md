# Justificación técnica – Unidad 3 (consumo seguro de APIs)

> Documento base. Cada integrante debe leerlo, verificarlo contra el código y ajustarlo con sus propias palabras: la guía exige que el código sea comprendido y justificado por el estudiante.

## 1. Consumo de APIs (criterio 3.1.1)
| Decisión | Justificación |
|---|---|
| `requests` con `timeout=(3, 8)` | Librería estándar de facto; sin timeout una API caída congelaría el programa. |
| `findic.cl` primero y `mindicador.cl` de respaldo (`servicios/api_indicadores.py`) | Ambas entregan el mismo JSON (`serie[{fecha, valor}]`); si la primera falla (p. ej. HTTP 500) se usa la segunda y se guarda en BD cuál fuente respondió. |
| Open-Meteo para el clima | Gratuita y sin llave de API; permite buscar por ciudad (geocodificación) y entrega temperatura, estado, humedad y pronóstico. Se eligió clima **por ciudad** porque los proyectos se ejecutan en distintos lugares; EcoTech instala paneles solares y hace proyectos ambientales, por eso se piden radiación, horas de sol, UV y ráfagas, no solo temperatura. |
| Rangos por año | La API entrega un año por consulta; se pide cada año del rango y se filtra por fecha. Máximo 5 años para no abusar del servicio. |
| UTM con día 1 | Es un valor mensual: se consulta el primer día del mes. |

## 2. Seguridad (criterio 3.1.2)
- Login con claves almacenadas como hash (PBKDF2-SHA256 con sal; los usuarios creados por script usan SHA-256), 3 intentos y claves ocultas con `*` (ya existía).
- **Control por rol** (`controlador/permisos.py`): solo `GERENTE_RRHH` usa las APIs. Se valida en la vista (el menú no aparece) **y** en el DTO (defensa en profundidad). Los roles desconocidos (p. ej. `USUARIO` antiguo) se tratan como `EMPLEADO` (mínimo privilegio).
- Validación de entradas: ciudad con regex solo de letras (evita inyectar `&`, `/`, `?` en la URL), país de 2 letras, fechas `DD-MM-AAAA` no futuras, rango ordenado, código de indicador contra lista blanca.
- Consultas SQL parametrizadas (`%s`), sin concatenar texto del usuario.
- No hay llaves de API en el código; si se usara una API con llave se leería de una variable de entorno.
- Se valida el tipo y rango de los datos recibidos (p. ej. humedad 0–100) y se descartan respuestas de más de 2 MB.

## 2b. Cifrado de datos sensibles
| Decisión | Justificación |
|---|---|
| Cifrar correo, sueldo y dirección **en la BD** (`dao/cifrado.py`, Fernet de `cryptography`) | Las claves ya eran hash, pero estos datos estaban en claro; cifrarlos en la BD protege también ante acceso directo (phpMyAdmin) del administrador. Fernet es cifrado autenticado: detecta datos alterados. |
| Descifrar solo al pedir el dato y solo si el rol lo permite (`Empleado.getCorreo()` etc. + `controlador/sesion.py`) | El administrador nunca tiene el dato en claro en memoria; sin sesión no se ve nada (falla cerrado). |
| Solo `GERENTE_RRHH` ve los datos (`permisos.puedeVerDatosSensibles`) | Requisito del profesor: el administrador los ve encriptados. |
| Huella `CORREOHASH` (HMAC-SHA256) | El cifrado es aleatorio, por lo que un `UNIQUE` sobre el correo cifrado no funciona; la huella mantiene correos únicos sin guardarlos en claro. |
| Clave fuera del código (`clave_cifrado.key` o variable de entorno) | La clave no está escrita en el código. **Limitación:** el repositorio incluye una clave de *demostración* para que los datos de ejemplo cifrados del script SQL se puedan leer; en producción debe reemplazarse y no subirse a git. |
| `[ENCRIPTADO]` ignorado al modificar | Evita que un admin que presiona ENTER sobrescriba el dato real con el texto de la máscara. |

Limitación: quien tenga la clave Y acceso a la BD puede leer los datos; no hay rotación de claves.

## 3. Manejo de errores (criterio 3.1.3)
- `servicios/http_seguro.py` centraliza `try/except` para `Timeout`, `SSLError`, `ConnectionError`, otros errores de `requests`, códigos HTTP distintos de 200 (404, 429, 5xx…) y JSON inválido; todo se convierte en `ErrorServicio` con mensaje genérico.
- El detalle técnico (URL, excepción) va a `ecotech_errores.log`, no a pantalla. También se quitó el detalle de las excepciones inesperadas y de la conexión a la BD.
- Un fallo de un indicador no detiene el resto (al elegir “Todos”) ni cierra el programa.

## 4. Revisión del código generado con IA (criterio 3.1.4)
Se usó IA para generar la primera versión de los clientes de API y los menús. Revisión crítica:

| Hallazgo en el código generado / ejemplo base | Decisión |
|---|---|
| El ejemplo base (`RequerimientosEvaluacion3.py`) hace `requests.get` sin `try/except` y sin validar el código HTTP. | **Modificado**: se agregó manejo completo de errores y timeout. |
| Mensajes de error mostraban `{ex}` (podían revelar host/usuario de la BD). | **Modificado**: mensaje genérico + log. |
| Armar la URL con texto del usuario. | **Descartado**: solo códigos de lista blanca y fechas ya parseadas. |
| Guardar cada valor con un `INSERT` suelto. | **Modificado**: `INSERT … ON DUPLICATE KEY UPDATE` en una sola transacción, evita duplicados. |
| Confiar en el JSON recibido. | **Modificado**: se valida estructura, tipos y rangos. |

Pendientes que el equipo debe revisar: rotación del log, y reemplazar el hash SHA-256 sin sal de los usuarios creados por script por PBKDF2 (la aplicación ya usa PBKDF2 para los usuarios que crea).
