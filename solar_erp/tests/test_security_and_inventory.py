import hashlib
import secrets
import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.cliente import Cliente
from app.models.herramienta import Herramienta
from app.models.inventario import Material
from app.models.proyecto import Proyecto
from app.models.trabajador import Trabajador
from app.models.usuario import Usuario
from app.services.services import AuthService, HerramientaService, InventarioService, MovimientoService
from app.utils.security import hash_password, password_needs_upgrade, verify_password


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = TestingSession()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_pbkdf2_password_hash_and_legacy_upgrade(self):
        hashed = hash_password("solar123")
        self.assertTrue(verify_password("solar123", hashed))
        self.assertFalse(password_needs_upgrade(hashed))

        salt = secrets.token_hex(16)
        legacy = f"{salt}:{hashlib.sha256(f'{salt}solar123'.encode('utf-8')).hexdigest()}"
        self.assertTrue(verify_password("solar123", legacy))
        self.assertTrue(password_needs_upgrade(legacy))

        user = Usuario(
            nombre="Admin",
            username="admin-test",
            password=legacy,
            rol="administrador",
            activo=True,
        )
        self.db.add(user)
        self.db.commit()

        autenticado = AuthService(self.db).login("admin-test", "solar123")
        self.assertIsNotNone(autenticado)
        self.assertFalse(password_needs_upgrade(autenticado.password))

    def test_merge_materials_and_block_oversold_stock(self):
        inventario = InventarioService(self.db)
        material = inventario.crear(
            nombre_material="Panel Solar 550W",
            categoria="Paneles Solares",
            unidad="unidad",
            cantidad_actual=5,
            stock_minimo=1,
            ubicacion="Bodega A",
            proveedor_id=None,
            precio_unitario=1000,
        )
        actualizado = inventario.crear(
            nombre_material="Panel Solar 550W",
            categoria="Paneles Solares",
            unidad="unidad",
            cantidad_actual=2,
            stock_minimo=2,
            ubicacion="Bodega A",
            proveedor_id=None,
            precio_unitario=1200,
            merge_if_exists=True,
        )
        self.assertEqual(actualizado.id, material.id)
        self.assertEqual(actualizado.cantidad_actual, 7)
        self.assertEqual(actualizado.precio_unitario, 1200)

        cliente = Cliente(nombre="Cliente Demo", identificacion="123", telefono="", email="", direccion="", observaciones="")
        self.db.add(cliente)
        self.db.flush()
        proyecto = Proyecto(nombre_proyecto="Proyecto Demo", cliente_id=cliente.id, fecha_inicio=date.today())
        self.db.add(proyecto)
        self.db.commit()

        movimientos = MovimientoService(self.db)
        with self.assertRaises(ValueError):
            movimientos.registrar_salida(
                proyecto_id=proyecto.id,
                fecha=date.today(),
                responsable="Tester",
                observaciones="",
                items=[(material.id, 8)],
            )

        self.db.refresh(material)
        self.assertEqual(material.cantidad_actual, 7)

        movimiento = movimientos.registrar_salida(
            proyecto_id=proyecto.id,
            fecha=date.today(),
            responsable="Tester",
            observaciones="",
            items=[(material.id, 3)],
        )
        self.assertIsNotNone(movimiento.id)
        self.db.refresh(material)
        self.assertEqual(material.cantidad_actual, 4)

    def test_tool_history_logs_assignment_return_and_maintenance(self):
        trabajador = Trabajador(nombre="Carlos Ruiz", cargo="Tecnico", telefono="123", estado="activo")
        self.db.add(trabajador)
        self.db.flush()

        servicio = HerramientaService(self.db)
        herramienta = servicio.crear(
            codigo="H-001",
            nombre="Taladro",
            categoria="Herramienta Electrica",
            marca="Bosch",
            modelo="X1",
            numero_serie="SER-1",
            estado="disponible",
            ubicacion="Bodega",
            observaciones="Nueva",
        )
        asignacion = servicio.asignar(herramienta.id, trabajador.id, "Entrega inicial")
        servicio.devolver(asignacion.id, "Recibida en bodega")
        herramienta = servicio.obtener(herramienta.id)
        servicio.actualizar(
            herramienta,
            codigo=herramienta.codigo,
            nombre=herramienta.nombre,
            categoria=herramienta.categoria,
            marca=herramienta.marca,
            modelo=herramienta.modelo,
            numero_serie=herramienta.numero_serie,
            estado="mantenimiento",
            ubicacion=herramienta.ubicacion,
            observaciones="Revision preventiva",
        )

        historial = servicio.historial_general()
        tipos = [registro.tipo_movimiento for registro in historial]
        self.assertIn("creacion", tipos)
        self.assertIn("asignacion", tipos)
        self.assertIn("devolucion", tipos)
        self.assertIn("mantenimiento", tipos)


if __name__ == "__main__":
    unittest.main()
