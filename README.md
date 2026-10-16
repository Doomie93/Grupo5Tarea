# ECOTECH
## Proyecto de Programación Orientada a Objetos Segura

### 1. Requisitos previos

Para ejecutar el proyecto, es necesario contar con los siguientes elementos:

- Un computador.
- Python instalado.
- La biblioteca PyMySQL, instalada mediante el siguiente comando:
  `pip install PyMySQL`
- XAMPP con el servidor Apache y el servicio de base de datos habilitados.

### 2. Configuración de los datos del usuario

Abra el archivo `mydb_ecotech.txt` y modifique las instrucciones `INSERT` con sus datos personales, según corresponda.

**Primer INSERT: Registro del empleado**

```sql
INSERT INTO EMPLEADO
(NOMBRE, APELLIDO, CORREO, FECHACONTRATO, SALARIO, DIRECCION, TELEFONO, IDDEPARTAMENTO)
VALUES
('Joakin', 'Briones', 'correo@gmail.com', CURDATE(), 99999, 'Recoleta', '123456789', NULL);
```

Reemplace los valores de nombre, apellido, correo electrónico, salario, dirección y teléfono por sus datos correspondientes.

**Segundo INSERT: Creación del usuario**

```sql
INSERT INTO USUARIO
(NOMBREUSUARIO, CLAVE, ROL, IDEMPLEADO)
VALUES
('pepe', SHA2('12345', 256), 'ADMINISTRADOR', LAST_INSERT_ID());
```

Modifique el nombre de usuario y la contraseña según sus preferencias. La función `SHA2` permite almacenar la contraseña mediante su hash SHA-256.

**Importante:** ejecute ambos INSERT en el orden indicado y dentro de la misma conexión para que `LAST_INSERT_ID()` asigne correctamente el identificador del empleado recién creado.

### 3. Configuración de XAMPP y la base de datos

1. Abra el panel de control de XAMPP e inicie los servicios Apache y MySQL (o MariaDB, según la versión instalada).
2. Abra su navegador e ingrese a [http://localhost/](http://localhost/).
3. Acceda a phpMyAdmin para administrar las bases de datos.
4. Consulte el archivo `conex/config.py` para identificar el nombre de la base de datos y los demás parámetros de conexión configurados para el proyecto.
5. Cree la base de datos utilizando el nombre y la configuración correspondientes.

### 4. Ejecución del script SQL

1. Ingrese a la base de datos que acaba de crear desde phpMyAdmin.
2. Seleccione la pestaña **SQL**.
3. Abra el archivo `mydb_ecotech.txt` y copie todo su contenido.
4. Pegue el contenido en el editor SQL de phpMyAdmin.
5. Revise las instrucciones y ejecútelas para crear las estructuras necesarias e insertar los datos iniciales.

### 5. Verificación final

Una vez ejecutado el script, compruebe que las tablas se hayan creado correctamente y que los registros del empleado y del usuario estén presentes en la base de datos.

Con estos pasos, la base de datos quedará preparada para utilizarse con el proyecto ECOTECH.