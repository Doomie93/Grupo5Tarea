# Tarea culia
Proyecto de Programación Orientada a Objeto Seguro.
### Requerimientos
- `computador`
- `python`
- `pip install PyMySQL`
- `Apache XAMPP`
### Instrucciones
Edita en archivo `mydb_ecotech.txt` los 2 inserts con tus datos:

      insert into EMPLEADO (NOMBRE, APELLIDO, CORREO, FECHACONTRATO, SALARIO, DIRECCION, TELEFONO, IDDEPARTAMENTO)
      values ('Joakin', 'Briones', 'correo@gmail.com', curdate(), 9999999999, 'Recoleta', '123456789', null);
               ^^^^^^    ^^^^^^^    ^^^^^^^^^^^^^^^^              ^^^^^^^^^^   ^^^^^^^^    ^^^^^^^^^
      insert into USUARIO (NOMBREUSUARIO, CLAVE, ROL, IDEMPLEADO)
      values ('pepe', SHA2('12345', 256), 'ADMINISTRADOR', last_insert_id());
               ^^^^         ^^^^^
Luego abre el XAMPP y entra a `https://localhost/`, crea la base de datos con los datos de `conex/config.py` y finalmente abre la base de datos y en el apartado **SQL** pega el contenido.
