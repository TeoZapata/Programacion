"""
RETIE Manager - Módulo de Base de Datos
Gestiona la conexión SQLite y el esquema de datos del sistema.
"""

import sqlite3
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime


DB_PATH = os.environ.get("RETIE_DB_PATH", str(Path.home() / "RETIE_Manager" / "retie.db"))


def get_connection() -> sqlite3.Connection:
    """Retorna una conexión a la base de datos SQLite con row_factory activado."""
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def hash_password(password: str) -> str:
    """Genera hash SHA-256 de una contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()


def initialize_database():
    """Crea todas las tablas si no existen e inserta datos iniciales."""
    conn = get_connection()
    cur = conn.cursor()

    # --- Tabla: usuarios ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre_completo TEXT,
            rol TEXT DEFAULT 'ingeniero',  -- 'administrador' | 'ingeniero'
            activo INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # --- Tabla: ingenieros (configuración del profesional) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ingenieros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER UNIQUE,
            nombre TEXT,
            cedula TEXT,
            matricula_profesional TEXT,
            empresa TEXT,
            nit TEXT,
            direccion TEXT,
            telefono TEXT,
            correo TEXT,
            firma_path TEXT,
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # --- Tabla: clientes ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula_nit TEXT,
            direccion TEXT,
            telefono TEXT,
            correo TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # --- Tabla: proyectos ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cliente_id INTEGER,
            tipo TEXT DEFAULT 'electrico',  -- 'electrico' | 'fotovoltaico'
            direccion TEXT,
            ciudad TEXT,
            departamento TEXT,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            consumo_kwh_mes REAL DEFAULT 0,
            estado TEXT DEFAULT 'activo',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    # --- Tabla: sistemas fotovoltaicos ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sistemas_fotovoltaicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER UNIQUE,
            -- Paneles
            cantidad_paneles INTEGER DEFAULT 0,
            potencia_panel REAL DEFAULT 0,
            marca_panel TEXT,
            referencia_panel TEXT,
            -- Inversores
            cantidad_inversores INTEGER DEFAULT 0,
            marca_inversor TEXT,
            referencia_inversor TEXT,
            potencia_inversor REAL DEFAULT 0,
            -- Datos eléctricos
            calibre_conductor TEXT,
            tipo_conductor TEXT,
            proteccion_breaker TEXT,
            -- Cálculos
            potencia_total_kwp REAL DEFAULT 0,
            generacion_estimada_kwh REAL DEFAULT 0,
            irradiacion_zona REAL DEFAULT 4.5,
            eficiencia_sistema REAL DEFAULT 0.80,
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
        )
    """)

    # --- Tabla: imágenes del proyecto ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS imagenes_proyecto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            tipo TEXT,  -- 'ubicacion'|'cuadro_cargas'|'caida_tension'|'diagrama_unifilar'|'otro'
            nombre_archivo TEXT,
            ruta TEXT,
            descripcion TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
        )
    """)

    # --- Tabla: plantillas de documentos ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS plantillas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT,  -- 'acta_inicio'|'declaracion_construccion'|'declaracion_diseno'|'memoria_calculo'|'otro'
            ruta_archivo TEXT,
            descripcion TEXT,
            activa INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # --- Tabla: documentos generados ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documentos_generados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER,
            plantilla_id INTEGER,
            nombre_documento TEXT,
            ruta_archivo TEXT,
            fecha_generacion TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (proyecto_id) REFERENCES proyectos(id),
            FOREIGN KEY (plantilla_id) REFERENCES plantillas(id)
        )
    """)

    # --- Usuario administrador por defecto ---
    cur.execute("SELECT id FROM usuarios WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO usuarios (username, password_hash, nombre_completo, rol)
            VALUES (?, ?, ?, ?)
        """, ('admin', hash_password('admin123'), 'Administrador del Sistema', 'administrador'))
        admin_id = cur.lastrowid
        cur.execute("""
            INSERT INTO ingenieros (usuario_id, nombre, empresa)
            VALUES (?, ?, ?)
        """, (admin_id, 'Administrador', 'Mi Empresa'))

    conn.commit()
    conn.close()
    return True


# ─── CRUD helpers ────────────────────────────────────────────────

class UsuarioDAO:
    @staticmethod
    def autenticar(username: str, password: str):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM usuarios WHERE username=? AND password_hash=? AND activo=1",
            (username, hash_password(password))
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def listar():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM usuarios ORDER BY nombre_completo").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def crear(username, password, nombre_completo, rol='ingeniero'):
        conn = get_connection()
        try:
            cur = conn.execute(
                "INSERT INTO usuarios (username, password_hash, nombre_completo, rol) VALUES (?,?,?,?)",
                (username, hash_password(password), nombre_completo, rol)
            )
            uid = cur.lastrowid
            conn.execute("INSERT INTO ingenieros (usuario_id, nombre) VALUES (?,?)", (uid, nombre_completo))
            conn.commit()
            return uid
        finally:
            conn.close()

    @staticmethod
    def cambiar_password(user_id: int, nueva: str):
        conn = get_connection()
        conn.execute("UPDATE usuarios SET password_hash=? WHERE id=?", (hash_password(nueva), user_id))
        conn.commit()
        conn.close()


class IngenieroDAO:
    @staticmethod
    def obtener(usuario_id: int):
        conn = get_connection()
        row = conn.execute("SELECT * FROM ingenieros WHERE usuario_id=?", (usuario_id,)).fetchone()
        conn.close()
        return dict(row) if row else {}

    @staticmethod
    def guardar(usuario_id: int, datos: dict):
        conn = get_connection()
        datos['updated_at'] = datetime.now().isoformat()
        row = conn.execute("SELECT id FROM ingenieros WHERE usuario_id=?", (usuario_id,)).fetchone()
        if row:
            sets = ", ".join(f"{k}=?" for k in datos if k != 'id')
            vals = [datos[k] for k in datos if k != 'id'] + [usuario_id]
            conn.execute(f"UPDATE ingenieros SET {sets} WHERE usuario_id=?", vals)
        else:
            datos['usuario_id'] = usuario_id
            cols = ", ".join(datos.keys())
            phs = ", ".join("?" * len(datos))
            conn.execute(f"INSERT INTO ingenieros ({cols}) VALUES ({phs})", list(datos.values()))
        conn.commit()
        conn.close()


class ClienteDAO:
    @staticmethod
    def listar():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM clientes ORDER BY nombre").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def obtener(cliente_id: int):
        conn = get_connection()
        row = conn.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,)).fetchone()
        conn.close()
        return dict(row) if row else {}

    @staticmethod
    def guardar(datos: dict) -> int:
        conn = get_connection()
        datos['updated_at'] = datetime.now().isoformat()
        cid = datos.pop('id', None)
        if cid:
            sets = ", ".join(f"{k}=?" for k in datos)
            conn.execute(f"UPDATE clientes SET {sets} WHERE id=?", list(datos.values()) + [cid])
        else:
            datos['created_at'] = datetime.now().isoformat()
            cols = ", ".join(datos.keys())
            phs = ", ".join("?" * len(datos))
            cur = conn.execute(f"INSERT INTO clientes ({cols}) VALUES ({phs})", list(datos.values()))
            cid = cur.lastrowid
        conn.commit()
        conn.close()
        return cid

    @staticmethod
    def eliminar(cliente_id: int):
        conn = get_connection()
        conn.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
        conn.commit()
        conn.close()


class ProyectoDAO:
    @staticmethod
    def listar(filtro: str = ""):
        conn = get_connection()
        q = """
            SELECT p.*, c.nombre as cliente_nombre
            FROM proyectos p
            LEFT JOIN clientes c ON p.cliente_id = c.id
        """
        params = []
        if filtro:
            q += " WHERE p.nombre LIKE ? OR c.nombre LIKE ?"
            params = [f"%{filtro}%", f"%{filtro}%"]
        q += " ORDER BY p.updated_at DESC"
        rows = conn.execute(q, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def obtener(proyecto_id: int):
        conn = get_connection()
        row = conn.execute("""
            SELECT p.*, c.nombre as cliente_nombre, c.cedula_nit as cliente_cedula,
                   c.direccion as cliente_direccion, c.telefono as cliente_telefono,
                   c.correo as cliente_correo
            FROM proyectos p LEFT JOIN clientes c ON p.cliente_id=c.id
            WHERE p.id=?
        """, (proyecto_id,)).fetchone()
        conn.close()
        return dict(row) if row else {}

    @staticmethod
    def guardar(datos: dict) -> int:
        conn = get_connection()
        datos['updated_at'] = datetime.now().isoformat()
        pid = datos.pop('id', None)
        if pid:
            sets = ", ".join(f"{k}=?" for k in datos)
            conn.execute(f"UPDATE proyectos SET {sets} WHERE id=?", list(datos.values()) + [pid])
        else:
            datos['created_at'] = datetime.now().isoformat()
            cols = ", ".join(datos.keys())
            phs = ", ".join("?" * len(datos))
            cur = conn.execute(f"INSERT INTO proyectos ({cols}) VALUES ({phs})", list(datos.values()))
            pid = cur.lastrowid
        conn.commit()
        conn.close()
        return pid

    @staticmethod
    def eliminar(proyecto_id: int):
        conn = get_connection()
        conn.execute("DELETE FROM sistemas_fotovoltaicos WHERE proyecto_id=?", (proyecto_id,))
        conn.execute("DELETE FROM imagenes_proyecto WHERE proyecto_id=?", (proyecto_id,))
        conn.execute("DELETE FROM documentos_generados WHERE proyecto_id=?", (proyecto_id,))
        conn.execute("DELETE FROM proyectos WHERE id=?", (proyecto_id,))
        conn.commit()
        conn.close()


class SistemaFVDAO:
    @staticmethod
    def obtener(proyecto_id: int):
        conn = get_connection()
        row = conn.execute("SELECT * FROM sistemas_fotovoltaicos WHERE proyecto_id=?", (proyecto_id,)).fetchone()
        conn.close()
        return dict(row) if row else {}

    @staticmethod
    def guardar(proyecto_id: int, datos: dict):
        conn = get_connection()
        datos['updated_at'] = datetime.now().isoformat()
        datos['proyecto_id'] = proyecto_id
        row = conn.execute("SELECT id FROM sistemas_fotovoltaicos WHERE proyecto_id=?", (proyecto_id,)).fetchone()
        if row:
            datos.pop('proyecto_id', None)
            sets = ", ".join(f"{k}=?" for k in datos)
            conn.execute(f"UPDATE sistemas_fotovoltaicos SET {sets} WHERE proyecto_id=?",
                         list(datos.values()) + [proyecto_id])
        else:
            cols = ", ".join(datos.keys())
            phs = ", ".join("?" * len(datos))
            conn.execute(f"INSERT INTO sistemas_fotovoltaicos ({cols}) VALUES ({phs})", list(datos.values()))
        conn.commit()
        conn.close()


class ImagenDAO:
    @staticmethod
    def listar(proyecto_id: int):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM imagenes_proyecto WHERE proyecto_id=?", (proyecto_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def guardar(datos: dict) -> int:
        conn = get_connection()
        cols = ", ".join(datos.keys())
        phs = ", ".join("?" * len(datos))
        cur = conn.execute(f"INSERT INTO imagenes_proyecto ({cols}) VALUES ({phs})", list(datos.values()))
        conn.commit()
        conn.close()
        return cur.lastrowid

    @staticmethod
    def eliminar(imagen_id: int):
        conn = get_connection()
        conn.execute("DELETE FROM imagenes_proyecto WHERE id=?", (imagen_id,))
        conn.commit()
        conn.close()


class PlantillaDAO:
    @staticmethod
    def listar():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM plantillas WHERE activa=1 ORDER BY nombre").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def guardar(datos: dict) -> int:
        conn = get_connection()
        cols = ", ".join(datos.keys())
        phs = ", ".join("?" * len(datos))
        cur = conn.execute(f"INSERT INTO plantillas ({cols}) VALUES ({phs})", list(datos.values()))
        conn.commit()
        conn.close()
        return cur.lastrowid

    @staticmethod
    def eliminar(plantilla_id: int):
        conn = get_connection()
        conn.execute("UPDATE plantillas SET activa=0 WHERE id=?", (plantilla_id,))
        conn.commit()
        conn.close()


class DocumentoDAO:
    @staticmethod
    def listar(proyecto_id: int):
        conn = get_connection()
        rows = conn.execute("""
            SELECT d.*, p.nombre as plantilla_nombre
            FROM documentos_generados d
            LEFT JOIN plantillas p ON d.plantilla_id=p.id
            WHERE d.proyecto_id=?
            ORDER BY d.fecha_generacion DESC
        """, (proyecto_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def registrar(datos: dict) -> int:
        conn = get_connection()
        cols = ", ".join(datos.keys())
        phs = ", ".join("?" * len(datos))
        cur = conn.execute(f"INSERT INTO documentos_generados ({cols}) VALUES ({phs})", list(datos.values()))
        conn.commit()
        conn.close()
        return cur.lastrowid
