from sqlalchemy.orm import Session
from app.repositories.repositories import (
    ClienteRepository, ProveedorRepository, TrabajadorRepository,
    ProyectoRepository, MaterialRepository, MovimientoRepository, UsuarioRepository
)
from app.models.cliente import Cliente
from app.models.proveedor import Proveedor
from app.models.trabajador import Trabajador
from app.models.proyecto import Proyecto
from app.models.inventario import Material
from app.models.movimiento import MovimientoInventario, DetalleMovimiento
from app.models.usuario import Usuario
from app.utils.security import verify_password, hash_password


class AuthService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    def login(self, username: str, password: str):
        user = self.repo.get_by_username(username)
        if user and user.activo and verify_password(password, user.password):
            return user
        return None

    def get_all(self):
        return self.repo.get_all()

    def crear_usuario(self, nombre, username, password, rol):
        u = Usuario(nombre=nombre, username=username,
                    password=hash_password(password), rol=rol, activo=True)
        return self.repo.create(u)

    def actualizar_usuario(self, u: Usuario, nombre, rol, activo, nueva_password=None):
        u.nombre = nombre
        u.rol = rol
        u.activo = activo
        if nueva_password:
            u.password = hash_password(nueva_password)
        return self.repo.update(u)

    def eliminar(self, id):
        return self.repo.delete(id)


class ClienteService:
    def __init__(self, db: Session):
        self.repo = ClienteRepository(db)

    def listar(self):
        return self.repo.get_all()

    def buscar(self, texto):
        return self.repo.buscar(texto)

    def obtener(self, id):
        return self.repo.get_by_id(id)

    def crear(self, nombre, identificacion, telefono, email, direccion, observaciones):
        c = Cliente(nombre=nombre, identificacion=identificacion,
                    telefono=telefono, email=email, direccion=direccion,
                    observaciones=observaciones)
        return self.repo.create(c)

    def actualizar(self, c: Cliente, nombre, identificacion, telefono, email, direccion, observaciones):
        c.nombre = nombre
        c.identificacion = identificacion
        c.telefono = telefono
        c.email = email
        c.direccion = direccion
        c.observaciones = observaciones
        return self.repo.update(c)

    def eliminar(self, id):
        return self.repo.delete(id)


class ProveedorService:
    def __init__(self, db: Session):
        self.repo = ProveedorRepository(db)

    def listar(self):
        return self.repo.get_all()

    def buscar(self, texto):
        return self.repo.buscar(texto)

    def obtener(self, id):
        return self.repo.get_by_id(id)

    def crear(self, nombre, nit, telefono, email, direccion):
        p = Proveedor(nombre=nombre, nit=nit, telefono=telefono,
                      email=email, direccion=direccion)
        return self.repo.create(p)

    def actualizar(self, p: Proveedor, nombre, nit, telefono, email, direccion):
        p.nombre = nombre
        p.nit = nit
        p.telefono = telefono
        p.email = email
        p.direccion = direccion
        return self.repo.update(p)

    def eliminar(self, id):
        return self.repo.delete(id)


class TrabajadorService:
    def __init__(self, db: Session):
        self.repo = TrabajadorRepository(db)

    def listar(self):
        return self.repo.get_all()

    def buscar(self, texto):
        return self.repo.buscar(texto)

    def obtener(self, id):
        return self.repo.get_by_id(id)

    def crear(self, nombre, cargo, telefono, estado):
        t = Trabajador(nombre=nombre, cargo=cargo, telefono=telefono, estado=estado)
        return self.repo.create(t)

    def actualizar(self, t: Trabajador, nombre, cargo, telefono, estado):
        t.nombre = nombre
        t.cargo = cargo
        t.telefono = telefono
        t.estado = estado
        return self.repo.update(t)

    def eliminar(self, id):
        return self.repo.delete(id)


class ProyectoService:
    def __init__(self, db: Session):
        self.repo = ProyectoRepository(db)

    def listar(self):
        return self.repo.get_all_con_cliente()

    def buscar(self, texto):
        return self.repo.buscar(texto)

    def obtener(self, id):
        return self.repo.get_by_id(id)

    def count_activos(self):
        return self.repo.count_activos()

    def recientes(self, n=5):
        todos = self.repo.get_all_con_cliente()
        return sorted(todos, key=lambda x: x.creado_en, reverse=True)[:n]

    def crear(self, nombre_proyecto, cliente_id, direccion, fecha_inicio, estado,
              cantidad_paneles, potencia_panel, potencia_total_ac, modelo_inversor, cantidad_inversores):
        p = Proyecto(
            nombre_proyecto=nombre_proyecto,
            cliente_id=cliente_id,
            direccion=direccion,
            fecha_inicio=fecha_inicio,
            estado=estado,
            cantidad_paneles=cantidad_paneles,
            potencia_panel=potencia_panel,
            potencia_total_ac=potencia_total_ac,
            modelo_inversor=modelo_inversor,
            cantidad_inversores=cantidad_inversores,
        )
        p.calcular_potencia_dc()
        return self.repo.create(p)

    def actualizar(self, p: Proyecto, nombre_proyecto, cliente_id, direccion, fecha_inicio, estado,
                   cantidad_paneles, potencia_panel, potencia_total_ac, modelo_inversor, cantidad_inversores):
        p.nombre_proyecto = nombre_proyecto
        p.cliente_id = cliente_id
        p.direccion = direccion
        p.fecha_inicio = fecha_inicio
        p.estado = estado
        p.cantidad_paneles = cantidad_paneles
        p.potencia_panel = potencia_panel
        p.potencia_total_ac = potencia_total_ac
        p.modelo_inversor = modelo_inversor
        p.cantidad_inversores = cantidad_inversores
        p.calcular_potencia_dc()
        return self.repo.update(p)

    def eliminar(self, id):
        return self.repo.delete(id)


class InventarioService:
    def __init__(self, db: Session):
        self.repo = MaterialRepository(db)
        self.db   = db

    def listar(self):
        return self.repo.get_all()

    def buscar(self, texto):
        return self.repo.buscar(texto)

    def obtener(self, id):
        return self.repo.get_by_id(id)

    def stock_bajo(self):
        return self.repo.get_stock_bajo()

    def count_stock_bajo(self):
        return self.repo.count_stock_bajo()

    def valor_total_inventario(self):
        """Suma precio_unitario × cantidad_actual de TODOS los materiales (sin límite)."""
        from sqlalchemy import func
        from app.models.inventario import Material
        # Suma directa en BD para evitar el limit=500 de get_all
        result = self.db.query(
            func.sum(Material.precio_unitario * Material.cantidad_actual)
        ).scalar()
        return round(result or 0.0, 2)

    def crear(self, nombre_material, categoria, unidad, cantidad_actual,
              stock_minimo, ubicacion, proveedor_id, precio_unitario=0.0):
        m = Material(
            nombre_material=nombre_material, categoria=categoria, unidad=unidad,
            cantidad_actual=cantidad_actual, stock_minimo=stock_minimo,
            precio_unitario=precio_unitario or 0.0,
            ubicacion=ubicacion, proveedor_id=proveedor_id or None
        )
        return self.repo.create(m)

    def actualizar(self, m: Material, nombre_material, categoria, unidad,
                   cantidad_actual, stock_minimo, ubicacion, proveedor_id,
                   precio_unitario=None):
        m.nombre_material = nombre_material
        m.categoria       = categoria
        m.unidad          = unidad
        m.cantidad_actual = cantidad_actual
        m.stock_minimo    = stock_minimo
        m.ubicacion       = ubicacion
        m.proveedor_id    = proveedor_id or None
        if precio_unitario is not None:
            m.precio_unitario = precio_unitario
        return self.repo.update(m)

    def eliminar(self, id):
        return self.repo.delete(id)


class MovimientoService:
    def __init__(self, db: Session):
        self.repo     = MovimientoRepository(db)
        self.mat_repo = MaterialRepository(db)
        self.db       = db

    def ultimos(self, n=10):
        return self.repo.get_ultimos(n)

    def por_proyecto(self, proyecto_id):
        return self.repo.get_por_proyecto(proyecto_id)

    def _registrar_salida_proyecto(self, movimiento, mat, cantidad, tipo):
        """Crea un registro en salidas_proyecto con valor monetario."""
        from app.models.salida_proyecto import SalidaProyecto
        if not movimiento.proyecto_id:
            return
        precio = mat.precio_unitario or 0.0
        # Para devolución el valor es negativo (descuenta del acumulado)
        valor = round(cantidad * precio, 2)
        if tipo == "devolucion":
            valor = -valor
        sp = SalidaProyecto(
            proyecto_id     = movimiento.proyecto_id,
            movimiento_id   = movimiento.id,
            material_id     = mat.id,
            tipo            = tipo,
            cantidad        = cantidad,
            precio_unitario = precio,
            valor_total     = valor,
            fecha           = movimiento.fecha,
            responsable     = movimiento.responsable,
        )
        self.db.add(sp)

    def registrar_entrada(self, proveedor_id, factura, fecha, responsable, observaciones, items):
        """items: list of (material_id, cantidad, precio_unitario)"""
        mov = MovimientoInventario(
            tipo="entrada", proveedor_id=proveedor_id, factura=factura,
            fecha=fecha, responsable=responsable, observaciones=observaciones,
        )
        self.db.add(mov)
        self.db.flush()
        for mat_id, cantidad, precio in items:
            self.db.add(DetalleMovimiento(
                movimiento_id=mov.id, material_id=mat_id,
                cantidad=cantidad, precio_unitario=precio,
            ))
            mat = self.mat_repo.get_by_id(mat_id)
            if mat:
                mat.cantidad_actual += cantidad
                # Actualiza precio unitario del inventario con el último precio registrado
                if precio and precio > 0:
                    mat.precio_unitario = precio
        self.db.commit()
        self.db.refresh(mov)
        return mov

    def registrar_salida(self, proyecto_id, fecha, responsable, observaciones, items):
        """items: list of (material_id, cantidad)"""
        mov = MovimientoInventario(
            tipo="salida", proyecto_id=proyecto_id, fecha=fecha,
            responsable=responsable, observaciones=observaciones,
        )
        self.db.add(mov)
        self.db.flush()
        for mat_id, cantidad in items:
            mat = self.mat_repo.get_by_id(mat_id)
            precio = mat.precio_unitario if mat else 0.0
            self.db.add(DetalleMovimiento(
                movimiento_id=mov.id, material_id=mat_id,
                cantidad=cantidad, precio_unitario=precio,
            ))
            if mat:
                mat.cantidad_actual = max(0, mat.cantidad_actual - cantidad)
                self._registrar_salida_proyecto(mov, mat, cantidad, "salida")
        self.db.commit()
        self.db.refresh(mov)
        return mov

    def registrar_devolucion(self, proyecto_id, fecha, responsable, observaciones, items):
        """items: list of (material_id, cantidad)"""
        mov = MovimientoInventario(
            tipo="devolucion", proyecto_id=proyecto_id, fecha=fecha,
            responsable=responsable, observaciones=observaciones,
        )
        self.db.add(mov)
        self.db.flush()
        for mat_id, cantidad in items:
            mat = self.mat_repo.get_by_id(mat_id)
            precio = mat.precio_unitario if mat else 0.0
            self.db.add(DetalleMovimiento(
                movimiento_id=mov.id, material_id=mat_id,
                cantidad=cantidad, precio_unitario=precio,
            ))
            if mat:
                mat.cantidad_actual += cantidad
                self._registrar_salida_proyecto(mov, mat, cantidad, "devolucion")
        self.db.commit()
        self.db.refresh(mov)
        return mov

    # ── Consultas financieras por proyecto ───────────────────────────────────
    def resumen_financiero_proyecto(self, proyecto_id):
        """Retorna dict con totales de salidas, devoluciones y neto por proyecto."""
        from app.models.salida_proyecto import SalidaProyecto
        registros = (self.db.query(SalidaProyecto)
                     .filter(SalidaProyecto.proyecto_id == proyecto_id)
                     .all())
        salidas    = sum(r.valor_total for r in registros if r.tipo == "salida")
        devoluc    = sum(abs(r.valor_total) for r in registros if r.tipo == "devolucion")
        return {
            "salidas":     round(salidas, 2),
            "devoluciones": round(devoluc, 2),
            "neto":        round(salidas - devoluc, 2),
            "registros":   registros,
        }

    def resumen_todos_proyectos(self):
        """Lista de dicts {proyecto_id, nombre, salidas, devoluciones, neto}."""
        from app.models.salida_proyecto import SalidaProyecto
        from app.models.proyecto import Proyecto
        from sqlalchemy import func as sqlfunc
        rows = (self.db.query(
                    SalidaProyecto.proyecto_id,
                    Proyecto.nombre_proyecto,
                    sqlfunc.sum(SalidaProyecto.valor_total).label("neto"),
                )
                .join(Proyecto, Proyecto.id == SalidaProyecto.proyecto_id)
                .group_by(SalidaProyecto.proyecto_id, Proyecto.nombre_proyecto)
                .order_by(sqlfunc.sum(SalidaProyecto.valor_total).desc())
                .all())
        return [{"proyecto_id": r.proyecto_id, "nombre": r.nombre_proyecto,
                 "neto": round(r.neto, 2)} for r in rows]


# ─── HerramientaService ───────────────────────────────────────────────────────
from app.repositories.repositories import HerramientaRepository, AsignacionRepository
from app.models.herramienta import Herramienta, AsignacionHerramienta
from app.models.trabajador import Trabajador
from datetime import datetime


class HerramientaService:
    def __init__(self, db):
        self.db   = db
        self.repo = HerramientaRepository(db)
        self.asig = AsignacionRepository(db)

    def listar(self):
        return self.repo.get_all()

    def buscar(self, texto):
        return self.repo.buscar(texto)

    def obtener(self, id):
        return self.repo.get_by_id(id)

    def crear(self, codigo, nombre, categoria, marca, modelo, numero_serie,
              estado, ubicacion, observaciones):
        h = Herramienta(
            codigo=codigo or None, nombre=nombre, categoria=categoria,
            marca=marca, modelo=modelo, numero_serie=numero_serie,
            estado=estado, ubicacion=ubicacion, observaciones=observaciones
        )
        return self.repo.create(h)

    def actualizar(self, h: Herramienta, codigo, nombre, categoria, marca,
                   modelo, numero_serie, estado, ubicacion, observaciones):
        h.codigo        = codigo or None
        h.nombre        = nombre
        h.categoria     = categoria
        h.marca         = marca
        h.modelo        = modelo
        h.numero_serie  = numero_serie
        h.estado        = estado
        h.ubicacion     = ubicacion
        h.observaciones = observaciones
        return self.repo.update(h)

    def eliminar(self, id):
        return self.repo.delete(id)

    # ── Asignaciones ──────────────────────────────────────────────────────────
    def asignar(self, herramienta_id, trabajador_id, observaciones=""):
        herr = self.obtener(herramienta_id)
        if not herr:
            raise ValueError("Herramienta no encontrada")
        if herr.estado == "asignada":
            raise ValueError("La herramienta ya está asignada a otro trabajador")
        a = AsignacionHerramienta(
            herramienta_id=herramienta_id,
            trabajador_id=trabajador_id,
            estado="activa",
            observaciones=observaciones
        )
        herr.estado = "asignada"
        self.repo.update(herr)
        return self.asig.create(a)

    def devolver(self, asignacion_id, observaciones=""):
        a = self.asig.get_by_id(asignacion_id)
        if not a:
            raise ValueError("Asignación no encontrada")
        a.estado = "devuelta"
        a.fecha_devolucion = datetime.now()
        if observaciones:
            a.observaciones = (a.observaciones or "") + f" | Devolución: {observaciones}"
        self.asig.update(a)
        # Liberar herramienta
        herr = self.obtener(a.herramienta_id)
        if herr:
            herr.estado = "disponible"
            self.repo.update(herr)
        return a

    def asignaciones_activas_trabajador(self, trabajador_id):
        return self.asig.get_activas_por_trabajador(trabajador_id)

    def todas_asignaciones_activas(self):
        return self.asig.get_todas_activas()

    def historial_herramienta(self, herramienta_id):
        return self.asig.get_historial_herramienta(herramienta_id)

    def todas_asignaciones(self):
        return self.asig.get_all_con_relaciones()


# ─── PedidoCompraService ─────────────────────────────────────────────────────
from app.models.pedido import PedidoCompra, DetallePedido


class PedidoCompraService:
    def __init__(self, db: Session):
        self.db = db

    def registrar(self, solicitante, proyecto_nombre, observaciones, ruta_pdf,
                  items_disponibles, items_comprar):
        """
        Crea un registro de PedidoCompra con todos sus detalles.
        items_disponibles / items_comprar: list of dicts con nombre, unidad, solicitado, disponible, (faltante)
        """
        from datetime import date as _date
        pedido = PedidoCompra(
            solicitante=solicitante,
            proyecto_nombre=proyecto_nombre,
            observaciones=observaciones,
            ruta_pdf=ruta_pdf,
            fecha=_date.today(),
        )
        self.db.add(pedido)
        self.db.flush()

        for it in items_disponibles:
            self.db.add(DetallePedido(
                pedido_id=pedido.id,
                nombre_material=it["nombre"],
                unidad=it.get("unidad", ""),
                cantidad_sol=it.get("solicitado", 0),
                stock_disp=it.get("disponible", 0),
                faltante=0,
                en_stock=True,
            ))
        for it in items_comprar:
            self.db.add(DetallePedido(
                pedido_id=pedido.id,
                nombre_material=it["nombre"],
                unidad=it.get("unidad", ""),
                cantidad_sol=it.get("solicitado", 0),
                stock_disp=it.get("disponible", 0),
                faltante=it.get("faltante", 0),
                en_stock=False,
            ))
        self.db.commit()
        return pedido

    def ultimos(self, n=20):
        return (self.db.query(PedidoCompra)
                .order_by(PedidoCompra.creado_en.desc())
                .limit(n).all())

    def get_by_id(self, id):
        return self.db.query(PedidoCompra).filter(PedidoCompra.id == id).first()

    def todos(self):
        return self.db.query(PedidoCompra).order_by(PedidoCompra.creado_en.desc()).all()


# ─── SalidaProyectoService ────────────────────────────────────────────────────
class SalidaProyectoService:
    def __init__(self, db: Session):
        self.db = db

    def por_proyecto(self, proyecto_id):
        from app.models.salida_proyecto import SalidaProyecto
        from sqlalchemy.orm import joinedload
        return (self.db.query(SalidaProyecto)
                .options(joinedload(SalidaProyecto.material),
                         joinedload(SalidaProyecto.movimiento))
                .filter(SalidaProyecto.proyecto_id == proyecto_id)
                .order_by(SalidaProyecto.fecha.desc())
                .all())

    def todos_proyectos_resumen(self):
        """
        Lista de proyectos con su acumulado financiero.
        Calcula totales en Python para evitar dependencias de case() entre versiones SQLAlchemy.
        """
        from app.models.salida_proyecto import SalidaProyecto
        from app.models.proyecto import Proyecto

        # Traer todos los registros con el nombre del proyecto
        registros = (self.db.query(SalidaProyecto, Proyecto.nombre_proyecto)
                     .join(Proyecto, Proyecto.id == SalidaProyecto.proyecto_id)
                     .order_by(SalidaProyecto.proyecto_id)
                     .all())

        # Agrupar en Python
        grupos = {}  # proyecto_id -> {nombre, salidas, devoluciones}
        for reg, nombre in registros:
            pid = reg.proyecto_id
            if pid not in grupos:
                grupos[pid] = {"nombre": nombre, "salidas": 0.0, "devoluciones": 0.0}
            if reg.tipo == "salida":
                grupos[pid]["salidas"] += reg.valor_total or 0
            elif reg.tipo == "devolucion":
                grupos[pid]["devoluciones"] += abs(reg.valor_total or 0)

        resultado = []
        for pid, g in grupos.items():
            salidas = round(g["salidas"], 2)
            devol   = round(g["devoluciones"], 2)
            resultado.append({
                "proyecto_id":   pid,
                "nombre":        g["nombre"],
                "total_salidas": salidas,
                "devoluciones":  devol,
                "neto":          round(salidas - devol, 2),
            })
        # Ordenar por neto descendente
        resultado.sort(key=lambda x: x["neto"], reverse=True)
        return resultado

    def valor_total_salidas(self):
        """Valor total neto de materiales entregados a proyectos."""
        from app.models.salida_proyecto import SalidaProyecto
        from sqlalchemy import func as sqlfunc
        result = self.db.query(sqlfunc.sum(SalidaProyecto.valor_total)).scalar()
        return round(result or 0, 2)


from app.services.core_services import *  # noqa: F401,F403,E402
