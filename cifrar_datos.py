"""Cifra ahora mismo los datos sensibles (correo, sueldo, dirección) que sigan en texto plano en la base de datos.
Uso:  python cifrar_datos.py      (es seguro ejecutarlo varias veces)"""
from dao.dao_empleado import EmpleadoDAO

if __name__ == "__main__":
    print(f"Filas cifradas: {EmpleadoDAO().cifrarPendientes()}")
