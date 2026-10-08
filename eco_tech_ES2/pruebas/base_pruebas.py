"""Fixture común: BD en memoria + controladores ensamblados."""
import unittest

from conex.conexion import Conexion
from main import construir_contexto
from modelo.usuario import ADMIN, EMPLEADO, GERENTE

PASS = "Clave1234"


class BaseConBD(unittest.TestCase):
    def setUp(self):
        self.cx = Conexion(":memory:")
        self.c = construir_contexto(self.cx)
        self.c.auth.registrar_primer_admin("admin", PASS)
        self.entrar("admin")

    def tearDown(self):
        self.cx.cerrar()

    def entrar(self, usuario, password=PASS):
        self.c.auth.cerrar_sesion()
        return self.c.auth.iniciar_sesion(usuario, password)

    def nuevo_empleado(self, rut="12345678-5", email="ana@eco.cl", tipo="PLANTA", salario=1000000):
        return self.c.empleados.registrar(tipo, rut, "Ana Pérez", email, salario)

    def nuevo_proyecto(self, nombre="Planta Solar"):
        return self.c.proyectos.crear(nombre, "2026-01-01", presupuesto=5000000)
