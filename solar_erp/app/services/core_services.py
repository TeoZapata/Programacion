from datetime import datetime

from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.herramienta import AsignacionHerramienta, Herramienta, HistorialHerramienta
from app.models.inventario import Material
from app.models.movimiento import DetalleMovimiento, MovimientoInventario
from app.models.pedido import DetallePedido, PedidoCompra
from app.models.proveedor import Proveedor
from app.models.proyecto import Proyecto
from app.models.trabajador import Trabajador
from app.models.usuario import Usuario
from app.repositories.repositories import (
    AsignacionRepository,
    ClienteRepository,
    HerramientaRepository,
    HistorialHerramientaRepository,
    MaterialRepository,
    MovimientoRepository,
    ProyectoRepository,
    ProveedorRepository,
    TrabajadorRepository,
    UsuarioRepository,
)
from app.utils.security import hash_password, password_needs_upgrade, verify_password


class ServiceMixin:
    def __init__(self, db: Session):
        self.db = db

    def _commit(self, obj=None):
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        if obj is not None:
            self.db.refresh(obj)
        return obj


class AuthService(ServiceMixin):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repo = UsuarioRepository(db)

    def login(self, username: str, password: str):
        user = self.repo.get_by_username(username)
        if user and user.activo and verify_password(password, user.password):
            if password_needs_upgrade(user.password):
                user.password = hash_password(password)
                self._commit(user)
            return user
        return None

    def get_all(self):
        return self.repo.get_all()

    def crear_usuario(self, nombre, username, password, rol):
        u = Usuario(
            nombre=nombre,
            username=username,
            password=hash_password(password),
            rol=rol,
            activo=True,
        )
        self.repo.create(u)
        return self._commit(u)

    def actualizar_usuario(self, u: Usuario, nombre, rol, activo, nueva_password=None):
        u.nombre = nombre
        u.rol = rol
        u.activo = activo
        if nueva_password:
            u.password = hash_password(nueva_password)
        self.repo.update(u)
        return self._commit(u)

    def eliminar(self, id):
        obj = self.repo.delete(id)
        return self._commit() if obj else None


class ClienteService(ServiceMixin):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repo = ClienteRepository(db)

    def listar(self):
        return self.repo.get_all()

    def buscar(self, texto):
        return self.repo.buscar(texto)

    def obtener(self, id):
        return self.repo.get_by_id(id)

    def crear(self, nombre, identificacion, telefono, email, direccion, observaciones):
        c = Cliente(
            nombre=nombre,
            identificacion=identificacion,
            telefono=telefono,
            email=email,
            direccion=direccion,
            observaciones=observaciones,
        )
        self.repo.create(c)
        return self._commit(c)

    def actualizar(self, c: Cliente, nombre, identificacion, telefono, email, direccion, observaciones):
        c.nombre = nombre
        c.identificacion = identificacion
        c.telefono = telefono
        c.email = email
        c.direccion = direccion
        c.observaciones = observaciones
        self.repo.update(c)
        return self._commit(c)

    def eliminar(self, id):
        obj = self.repo.delete(id)
        return self._commit() if obj else None


class ProveedorService(ServiceMixin):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repo = ProveedorRepository(db)

    def listar(self):
        return self.repo.get_all()

    def buscar(self, texto):
        return self.repo.buscar(texto)

    def obtener(self, id):
        return self.repo.get_by_id(id)

    def crear(self, nombre, nit, telefono, email, direccion):
        p = Proveedor(nombre=nombre, nit=nit, telefono=telefono, email=email, direccion=direccion)
        self.repo.create(p)
        return self._commit(p)

    def actualizar(self, p: Proveedor, nombre, nit, telefono, email, direccion):
        p.nombre = nombre
        p.nit = nit
        p.telefono = telefono
        p.email = email
        p.direccion = direccion
        self.repo.update(p)
        return self._commit(p)

    def eliminar(self, id):
        obj = self.repo.delete(id)
        return self._commit() if obj else None


class TrabajadorService(ServiceMixin):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repo = TrabajadorRepository(db)

    def listar(self):
        return self.repo.get_all()

    def buscar(self, texto):
        return self.repo.buscar(texto)

    def obtener(self, id):
        return self.repo.get_by_id(id)

    def crear(self, nombre, cargo, telefono, estado):
        t = Trabajador(nombre=nombre, cargo=cargo, telefono=telefono, estado=estado)
        self.repo.create(t)
        return self._commit(t)

    def actualizar(self, t: Trabajador, nombre, cargo, telefono, estado):
        t.nombre = nombre
        t.cargo = cargo
        t.telefono = telefono
        t.estado = estado
        self.repo.update(t)
        return self._commit(t)

    def eliminar(self, id):
        obj = self.repo.delete(id)
        return self._commit() if obj else None


class ProyectoService(ServiceMixin):
    def __init__(self, db: Session):
        super().__init__(db)
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
        self.repo.create(p)
        return self._commit(p)

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
        self.repo.update(p)
        return self._commit(p)

    def eliminar(self, id):
        obj = self.repo.delete(id)
        return self._commit() if obj else None


class InventarioService(ServiceMixin):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repo = MaterialRepository(db)

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
        from sqlalchemy import func
        result = self.db.query(func.sum(Material.precio_unitario * Material.cantidad_actual)).scalar()
        return round(result or 0.0, 2)

    def crear(self, nombre_material, categoria, unidad, cantidad_actual,
              stock_minimo, ubicacion, proveedor_id, precio_unitario=0.0, merge_if_exists=False):
        existente = self.repo.get_by_nombre(nombre_material)
        if existente:
            if not merge_if_exists:
                raise ValueError(f"Ya existe un material con el nombre '{nombre_material}'.")
            existente.cantidad_actual += cantidad_actual
            existente.stock_minimo = max(existente.stock_minimo or 0, stock_minimo or 0)
            existente.categoria = categoria or existente.categoria
            existente.unidad = unidad or existente.unidad
            existente.ubicacion = ubicacion or existente.ubicacion
            existente.proveedor_id = proveedor_id or existente.proveedor_id
            if precio_unitario is not None and precio_unitario > 0:
                existente.precio_unitario = precio_unitario
            self.repo.update(existente)
            return self._commit(existente)

        m = Material(
            nombre_material=nombre_material,
            categoria=categoria,
            unidad=unidad,
            cantidad_actual=cantidad_actual,
            stock_minimo=stock_minimo,
            precio_unitario=precio_unitario or 0.0,
            ubicacion=ubicacion,
            proveedor_id=proveedor_id or None,
        )
        self.repo.create(m)
        return self._commit(m)

    def actualizar(self, m: Material, nombre_material, categoria, unidad,
                   cantidad_actual, stock_minimo, ubicacion, proveedor_id,
                   precio_unitario=None):
        m.nombre_material = nombre_material
        m.categoria = categoria
        m.unidad = unidad
        m.cantidad_actual = cantidad_actual
        m.stock_minimo = stock_minimo
        m.ubicacion = ubicacion
        m.proveedor_id = proveedor_id or None
        if precio_unitario is not None:
            m.precio_unitario = precio_unitario
        self.repo.update(m)
        return self._commit(m)

    def eliminar(self, id):
        obj = self.repo.delete(id)
        return self._commit() if obj else None


class MovimientoService(ServiceMixin):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repo = MovimientoRepository(db)
        self.mat_repo = MaterialRepository(db)

    def ultimos(self, n=10):
        return self.repo.get_ultimos(n)

    def por_proyecto(self, proyecto_id):
        return self.repo.get_por_proyecto(proyecto_id)

    def _validar_items(self, items, require_price=False):
        if not items:
            raise ValueError("Debes registrar al menos un material.")
        for item in items:
            if require_price:
                mat_id, cantidad, precio = item
                if precio is None or precio < 0:
                    raise ValueError("El precio unitario debe ser un numero positivo.")
            else:
                mat_id, cantidad = item
            if not mat_id:
                raise ValueError("Todos los items deben tener un material valido.")
            if cantidad is None or cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor que cero.")

    def _registrar_salida_proyecto(self, movimiento, mat, cantidad, tipo):
        from app.models.salida_proyecto import SalidaProyecto

        if not movimiento.proyecto_id:
            return
        precio = mat.precio_unitario or 0.0
        valor = round(cantidad * precio, 2)
        if tipo == "devolucion":
            valor = -valor
        self.db.add(SalidaProyecto(
            proyecto_id=movimiento.proyecto_id,
            movimiento_id=movimiento.id,
            material_id=mat.id,
            tipo=tipo,
            cantidad=cantidad,
            precio_unitario=precio,
            valor_total=valor,
            fecha=movimiento.fecha,
            responsable=movimiento.responsable,
        ))

    def registrar_entrada(self, proveedor_id, factura, fecha, responsable, observaciones, items):
        self._validar_items(items, require_price=True)
        mov = MovimientoInventario(
            tipo="entrada",
            proveedor_id=proveedor_id,
            factura=factura,
            fecha=fecha,
            responsable=responsable,
            observaciones=observaciones,
        )
        try:
            self.db.add(mov)
            self.db.flush()
            for mat_id, cantidad, precio in items:
                mat = self.mat_repo.get_by_id(mat_id)
                if not mat:
                    raise ValueError(f"Material no encontrado: {mat_id}")
                self.db.add(DetalleMovimiento(
                    movimiento_id=mov.id,
                    material_id=mat_id,
                    cantidad=cantidad,
                    precio_unitario=precio,
                ))
                mat.cantidad_actual += cantidad
                if precio > 0:
                    mat.precio_unitario = precio
            return self._commit(mov)
        except Exception:
            self.db.rollback()
            raise

    def registrar_salida(self, proyecto_id, fecha, responsable, observaciones, items):
        if not proyecto_id:
            raise ValueError("Selecciona un proyecto para registrar la salida.")
        self._validar_items(items)
        mov = MovimientoInventario(
            tipo="salida",
            proyecto_id=proyecto_id,
            fecha=fecha,
            responsable=responsable,
            observaciones=observaciones,
        )
        try:
            self.db.add(mov)
            self.db.flush()
            for mat_id, cantidad in items:
                mat = self.mat_repo.get_by_id(mat_id)
                if not mat:
                    raise ValueError(f"Material no encontrado: {mat_id}")
                disponible = mat.cantidad_actual or 0
                if cantidad > disponible:
                    raise ValueError(
                        f"Stock insuficiente para '{mat.nombre_material}'. Disponible: {disponible:g}, solicitado: {cantidad:g}."
                    )
                self.db.add(DetalleMovimiento(
                    movimiento_id=mov.id,
                    material_id=mat_id,
                    cantidad=cantidad,
                    precio_unitario=mat.precio_unitario or 0.0,
                ))
                mat.cantidad_actual = disponible - cantidad
                self._registrar_salida_proyecto(mov, mat, cantidad, "salida")
            return self._commit(mov)
        except Exception:
            self.db.rollback()
            raise

    def registrar_devolucion(self, proyecto_id, fecha, responsable, observaciones, items):
        self._validar_items(items)
        mov = MovimientoInventario(
            tipo="devolucion",
            proyecto_id=proyecto_id,
            fecha=fecha,
            responsable=responsable,
            observaciones=observaciones,
        )
        try:
            self.db.add(mov)
            self.db.flush()
            for mat_id, cantidad in items:
                mat = self.mat_repo.get_by_id(mat_id)
                if not mat:
                    raise ValueError(f"Material no encontrado: {mat_id}")
                self.db.add(DetalleMovimiento(
                    movimiento_id=mov.id,
                    material_id=mat_id,
                    cantidad=cantidad,
                    precio_unitario=mat.precio_unitario or 0.0,
                ))
                mat.cantidad_actual += cantidad
                self._registrar_salida_proyecto(mov, mat, cantidad, "devolucion")
            return self._commit(mov)
        except Exception:
            self.db.rollback()
            raise

    def resumen_financiero_proyecto(self, proyecto_id):
        from app.models.salida_proyecto import SalidaProyecto

        registros = self.db.query(SalidaProyecto).filter(SalidaProyecto.proyecto_id == proyecto_id).all()
        salidas = sum(r.valor_total for r in registros if r.tipo == "salida")
        devoluc = sum(abs(r.valor_total) for r in registros if r.tipo == "devolucion")
        return {
            "salidas": round(salidas, 2),
            "devoluciones": round(devoluc, 2),
            "neto": round(salidas - devoluc, 2),
            "registros": registros,
        }

    def resumen_todos_proyectos(self):
        from sqlalchemy import func as sqlfunc
        from app.models.proyecto import Proyecto
        from app.models.salida_proyecto import SalidaProyecto

        rows = (self.db.query(
                    SalidaProyecto.proyecto_id,
                    Proyecto.nombre_proyecto,
                    sqlfunc.sum(SalidaProyecto.valor_total).label("neto"),
                )
                .join(Proyecto, Proyecto.id == SalidaProyecto.proyecto_id)
                .group_by(SalidaProyecto.proyecto_id, Proyecto.nombre_proyecto)
                .order_by(sqlfunc.sum(SalidaProyecto.valor_total).desc())
                .all())
        return [
            {"proyecto_id": r.proyecto_id, "nombre": r.nombre_proyecto, "neto": round(r.neto, 2)}
            for r in rows
        ]


class HerramientaService(ServiceMixin):
    def __init__(self, db):
        super().__init__(db)
        self.repo = HerramientaRepository(db)
        self.asig = AsignacionRepository(db)
        self.historial_repo = HistorialHerramientaRepository(db)

    def listar(self):
        return self.repo.get_all()

    def buscar(self, texto):
        return self.repo.buscar(texto)

    def obtener(self, id):
        return self.repo.get_by_id(id)

    def crear(self, codigo, nombre, categoria, marca, modelo, numero_serie,
              estado, ubicacion, observaciones):
        h = Herramienta(
            codigo=codigo or None,
            nombre=nombre,
            categoria=categoria,
            marca=marca,
            modelo=modelo,
            numero_serie=numero_serie,
            estado=estado,
            ubicacion=ubicacion,
            observaciones=observaciones,
        )
        try:
            self.repo.create(h)
            self._registrar_historial(
                herramienta=h,
                tipo_movimiento="creacion",
                estado_anterior=None,
                estado_nuevo=h.estado,
                observaciones=observaciones or "Herramienta creada",
            )
            return self._commit(h)
        except Exception:
            self.db.rollback()
            raise

    def actualizar(self, h: Herramienta, codigo, nombre, categoria, marca,
                   modelo, numero_serie, estado, ubicacion, observaciones):
        estado_anterior = h.estado
        h.codigo = codigo or None
        h.nombre = nombre
        h.categoria = categoria
        h.marca = marca
        h.modelo = modelo
        h.numero_serie = numero_serie
        h.estado = estado
        h.ubicacion = ubicacion
        h.observaciones = observaciones
        try:
            self.repo.update(h)
            if estado_anterior != estado:
                tipo = "mantenimiento" if estado == "mantenimiento" else "cambio_estado"
                self._registrar_historial(
                    herramienta=h,
                    tipo_movimiento=tipo,
                    estado_anterior=estado_anterior,
                    estado_nuevo=estado,
                    observaciones=observaciones or "Cambio de estado manual",
                )
            return self._commit(h)
        except Exception:
            self.db.rollback()
            raise

    def eliminar(self, id):
        obj = self.repo.delete(id)
        return self._commit() if obj else None

    def asignar(self, herramienta_id, trabajador_id, observaciones=""):
        herr = self.obtener(herramienta_id)
        if not herr:
            raise ValueError("Herramienta no encontrada")
        if herr.estado == "asignada":
            raise ValueError("La herramienta ya esta asignada a otro trabajador")
        a = AsignacionHerramienta(
            herramienta_id=herramienta_id,
            trabajador_id=trabajador_id,
            estado="activa",
            observaciones=observaciones,
        )
        try:
            estado_anterior = herr.estado
            herr.estado = "asignada"
            self.repo.update(herr)
            self.asig.create(a)
            self._registrar_historial(
                herramienta=herr,
                trabajador_id=trabajador_id,
                tipo_movimiento="asignacion",
                estado_anterior=estado_anterior,
                estado_nuevo="asignada",
                observaciones=observaciones or "Herramienta asignada",
            )
            return self._commit(a)
        except Exception:
            self.db.rollback()
            raise

    def devolver(self, asignacion_id, observaciones=""):
        a = self.asig.get_by_id(asignacion_id)
        if not a:
            raise ValueError("Asignacion no encontrada")
        try:
            herr = self.obtener(a.herramienta_id)
            estado_anterior = herr.estado if herr else None
            a.estado = "devuelta"
            a.fecha_devolucion = datetime.now()
            if observaciones:
                a.observaciones = (a.observaciones or "") + f" | Devolucion: {observaciones}"
            self.asig.update(a)
            if herr:
                herr.estado = "disponible"
                self.repo.update(herr)
                self._registrar_historial(
                    herramienta=herr,
                    trabajador_id=a.trabajador_id,
                    tipo_movimiento="devolucion",
                    estado_anterior=estado_anterior,
                    estado_nuevo="disponible",
                    observaciones=observaciones or "Herramienta devuelta",
                )
            return self._commit(a)
        except Exception:
            self.db.rollback()
            raise

    def asignaciones_activas_trabajador(self, trabajador_id):
        return self.asig.get_activas_por_trabajador(trabajador_id)

    def todas_asignaciones_activas(self):
        return self.asig.get_todas_activas()

    def historial_herramienta(self, herramienta_id):
        return self.asig.get_historial_herramienta(herramienta_id)

    def todas_asignaciones(self):
        return self.asig.get_all_con_relaciones()

    def registrar_mantenimiento(self, herramienta_id, observaciones="", trabajador_id=None):
        herr = self.obtener(herramienta_id)
        if not herr:
            raise ValueError("Herramienta no encontrada")
        estado_anterior = herr.estado
        try:
            herr.estado = "mantenimiento"
            self.repo.update(herr)
            self._registrar_historial(
                herramienta=herr,
                trabajador_id=trabajador_id,
                tipo_movimiento="mantenimiento",
                estado_anterior=estado_anterior,
                estado_nuevo="mantenimiento",
                observaciones=observaciones or "Ingreso a mantenimiento",
            )
            return self._commit(herr)
        except Exception:
            self.db.rollback()
            raise

    def historial_general(self, fecha_desde=None, fecha_hasta=None, trabajador_id=None, herramienta_id=None):
        return self.historial_repo.listar_filtrado(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            trabajador_id=trabajador_id,
            herramienta_id=herramienta_id,
        )

    def _registrar_historial(self, herramienta, tipo_movimiento, estado_anterior=None,
                             estado_nuevo=None, observaciones="", trabajador_id=None):
        registro = HistorialHerramienta(
            herramienta_id=herramienta.id,
            trabajador_id=trabajador_id,
            tipo_movimiento=tipo_movimiento,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            observaciones=observaciones or "",
        )
        self.historial_repo.create(registro)
        return registro


class PedidoCompraService(ServiceMixin):
    def __init__(self, db: Session):
        super().__init__(db)

    def registrar(self, solicitante, proyecto_nombre, observaciones, ruta_pdf,
                  items_disponibles, items_comprar):
        from datetime import date as _date

        pedido = PedidoCompra(
            solicitante=solicitante,
            proyecto_nombre=proyecto_nombre,
            observaciones=observaciones,
            ruta_pdf=ruta_pdf,
            fecha=_date.today(),
        )
        try:
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
            return self._commit(pedido)
        except Exception:
            self.db.rollback()
            raise

    def ultimos(self, n=20):
        return self.db.query(PedidoCompra).order_by(PedidoCompra.creado_en.desc()).limit(n).all()

    def get_by_id(self, id):
        return self.db.query(PedidoCompra).filter(PedidoCompra.id == id).first()

    def todos(self):
        return self.db.query(PedidoCompra).order_by(PedidoCompra.creado_en.desc()).all()


class SalidaProyectoService(ServiceMixin):
    def __init__(self, db: Session):
        super().__init__(db)

    def por_proyecto(self, proyecto_id):
        from sqlalchemy.orm import joinedload
        from app.models.salida_proyecto import SalidaProyecto

        return (self.db.query(SalidaProyecto)
                .options(
                    joinedload(SalidaProyecto.material),
                    joinedload(SalidaProyecto.movimiento),
                )
                .filter(SalidaProyecto.proyecto_id == proyecto_id)
                .order_by(SalidaProyecto.fecha.desc())
                .all())

    def todos_proyectos_resumen(self):
        from app.models.proyecto import Proyecto
        from app.models.salida_proyecto import SalidaProyecto

        registros = (self.db.query(SalidaProyecto, Proyecto.nombre_proyecto)
                     .join(Proyecto, Proyecto.id == SalidaProyecto.proyecto_id)
                     .order_by(SalidaProyecto.proyecto_id)
                     .all())

        grupos = {}
        for reg, nombre in registros:
            pid = reg.proyecto_id
            if pid not in grupos:
                grupos[pid] = {"nombre": nombre, "salidas": 0.0, "devoluciones": 0.0}
            if reg.tipo == "salida":
                grupos[pid]["salidas"] += reg.valor_total or 0
            elif reg.tipo == "devolucion":
                grupos[pid]["devoluciones"] += abs(reg.valor_total or 0)

        resultado = []
        for pid, grupo in grupos.items():
            salidas = round(grupo["salidas"], 2)
            devol = round(grupo["devoluciones"], 2)
            resultado.append({
                "proyecto_id": pid,
                "nombre": grupo["nombre"],
                "total_salidas": salidas,
                "devoluciones": devol,
                "neto": round(salidas - devol, 2),
            })
        resultado.sort(key=lambda x: x["neto"], reverse=True)
        return resultado

    def valor_total_salidas(self):
        from sqlalchemy import func as sqlfunc
        from app.models.salida_proyecto import SalidaProyecto

        result = self.db.query(sqlfunc.sum(SalidaProyecto.valor_total)).scalar()
        return round(result or 0, 2)
