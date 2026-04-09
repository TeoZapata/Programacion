from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from app.repositories.base import BaseRepository
from app.models.cliente import Cliente
from app.models.proveedor import Proveedor
from app.models.trabajador import Trabajador
from app.models.proyecto import Proyecto
from app.models.inventario import Material
from app.models.movimiento import MovimientoInventario, DetalleMovimiento
from app.models.usuario import Usuario


class ClienteRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Cliente)

    def buscar(self, texto: str):
        return self.db.query(Cliente).filter(
            or_(
                Cliente.nombre.ilike(f"%{texto}%"),
                Cliente.identificacion.ilike(f"%{texto}%"),
                Cliente.email.ilike(f"%{texto}%"),
            )
        ).all()


class ProveedorRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Proveedor)

    def buscar(self, texto: str):
        return self.db.query(Proveedor).filter(
            or_(
                Proveedor.nombre.ilike(f"%{texto}%"),
                Proveedor.nit.ilike(f"%{texto}%"),
            )
        ).all()


class TrabajadorRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Trabajador)

    def buscar(self, texto: str):
        return self.db.query(Trabajador).filter(
            Trabajador.nombre.ilike(f"%{texto}%")
        ).all()


class ProyectoRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Proyecto)

    def get_all_con_cliente(self):
        return self.db.query(Proyecto).options(
            joinedload(Proyecto.cliente)
        ).all()

    def buscar(self, texto: str):
        return self.db.query(Proyecto).options(
            joinedload(Proyecto.cliente)
        ).join(Cliente).filter(
            or_(
                Proyecto.nombre_proyecto.ilike(f"%{texto}%"),
                Cliente.nombre.ilike(f"%{texto}%"),
                Proyecto.estado.ilike(f"%{texto}%"),
            )
        ).all()

    def get_activos(self):
        from sqlalchemy import or_
        return self.db.query(Proyecto).options(
            joinedload(Proyecto.cliente)
        ).filter(
            or_(
                Proyecto.estado.ilike("En ejecuci%"),
                Proyecto.estado.ilike("Aprobado"),
                Proyecto.estado.ilike("En dise%"),
            )
        ).all()

    def count_activos(self):
        # Incluye todos los estados que significan un proyecto en curso
        # Usa ilike para tolerar variaciones de tildes/capitalización
        from sqlalchemy import or_, func
        return self.db.query(Proyecto).filter(
            or_(
                Proyecto.estado.ilike("En ejecuci%"),   # "En ejecución" o "En ejecucion"
                Proyecto.estado.ilike("Aprobado"),
                Proyecto.estado.ilike("En dise%"),       # "En diseño" o "En diseno"
                Proyecto.estado.ilike("En Proceso"),
                Proyecto.estado.ilike("Activo"),
            )
        ).count()


class MaterialRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Material)

    def buscar(self, texto: str):
        return self.db.query(Material).filter(
            or_(
                Material.nombre_material.ilike(f"%{texto}%"),
                Material.categoria.ilike(f"%{texto}%"),
            )
        ).all()

    def get_stock_bajo(self):
        return self.db.query(Material).filter(
            Material.cantidad_actual <= Material.stock_minimo
        ).all()

    def count_stock_bajo(self):
        return self.db.query(Material).filter(
            Material.cantidad_actual <= Material.stock_minimo
        ).count()

    def get_by_nombre(self, nombre: str):
        nombre_normalizado = (nombre or "").strip().lower()
        if not nombre_normalizado:
            return None
        return self.db.query(Material).filter(
            func.lower(Material.nombre_material) == nombre_normalizado
        ).first()


class MovimientoRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, MovimientoInventario)

    def _base_query(self):
        """Query base que carga todas las relaciones en la misma sesion."""
        return self.db.query(MovimientoInventario).options(
            joinedload(MovimientoInventario.proyecto).joinedload(Proyecto.cliente),
            joinedload(MovimientoInventario.proveedor),
            joinedload(MovimientoInventario.detalles).joinedload(DetalleMovimiento.material),
        )

    def get_ultimos(self, limit=100):
        return self._base_query().order_by(
            MovimientoInventario.creado_en.desc()
        ).limit(limit).all()

    def get_por_proyecto(self, proyecto_id: int):
        return self._base_query().filter(
            MovimientoInventario.proyecto_id == proyecto_id
        ).all()

    def get_by_id(self, id: int):
        return self._base_query().filter(
            MovimientoInventario.id == id
        ).first()


class UsuarioRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Usuario)

    def get_by_username(self, username: str):
        return self.db.query(Usuario).filter(Usuario.username == username).first()


# ─── Herramienta ──────────────────────────────────────────────────────────────
from app.models.herramienta import Herramienta, AsignacionHerramienta, HistorialHerramienta
from sqlalchemy.orm import joinedload as _jl

class HerramientaRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Herramienta)

    def get_all(self):
        return self.db.query(Herramienta).order_by(Herramienta.nombre).all()

    def buscar(self, texto):
        t = f"%{texto}%"
        return self.db.query(Herramienta).filter(
            (Herramienta.nombre.ilike(t)) |
            (Herramienta.codigo.ilike(t)) |
            (Herramienta.categoria.ilike(t)) |
            (Herramienta.marca.ilike(t))
        ).order_by(Herramienta.nombre).all()

    def get_by_codigo(self, codigo):
        return self.db.query(Herramienta).filter(Herramienta.codigo == codigo).first()


class AsignacionRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, AsignacionHerramienta)

    def _q(self):
        return self.db.query(AsignacionHerramienta).options(
            _jl(AsignacionHerramienta.herramienta),
            _jl(AsignacionHerramienta.trabajador),
        )

    def get_activas_por_trabajador(self, trabajador_id):
        return self._q().filter(
            AsignacionHerramienta.trabajador_id == trabajador_id,
            AsignacionHerramienta.estado == "activa"
        ).all()

    def get_todas_activas(self):
        return self._q().filter(AsignacionHerramienta.estado == "activa").all()

    def get_historial_herramienta(self, herramienta_id):
        return self._q().filter(
            AsignacionHerramienta.herramienta_id == herramienta_id
        ).order_by(AsignacionHerramienta.fecha_asignacion.desc()).all()

    def get_all_con_relaciones(self):
        return self._q().order_by(AsignacionHerramienta.fecha_asignacion.desc()).all()


class HistorialHerramientaRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, HistorialHerramienta)

    def _q(self):
        return self.db.query(HistorialHerramienta).options(
            _jl(HistorialHerramienta.herramienta),
            _jl(HistorialHerramienta.trabajador),
        )

    def listar_filtrado(self, fecha_desde=None, fecha_hasta=None, trabajador_id=None, herramienta_id=None):
        q = self._q()
        if fecha_desde is not None:
            q = q.filter(HistorialHerramienta.fecha_evento >= fecha_desde)
        if fecha_hasta is not None:
            q = q.filter(HistorialHerramienta.fecha_evento <= fecha_hasta)
        if trabajador_id:
            q = q.filter(HistorialHerramienta.trabajador_id == trabajador_id)
        if herramienta_id:
            q = q.filter(HistorialHerramienta.herramienta_id == herramienta_id)
        return q.order_by(HistorialHerramienta.fecha_evento.desc()).all()
