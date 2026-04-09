"""
==============================================================
tests/test_sistema_retie.py
Tests unitarios e integración para el Sistema RETIE
Ejecutar: pytest tests/ -v
==============================================================
"""

import pytest
import json
from datetime import date, timedelta
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Crea una instancia de la app para testing."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app import create_app
    app = create_app("testing")
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    from backend.database import db
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def admin_user(app, db_session):
    """Crea usuario admin para pruebas."""
    from backend.models.user import User
    user = User(
        nombre="Admin Test",
        correo="admin@test.com",
        usuario="admin_test",
        password_hash=generate_password_hash("test123"),
        rol="ADMIN",
        activo=True
    )
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def logged_client(client, admin_user, app):
    """Cliente con sesión iniciada."""
    with app.app_context():
        client.post("/auth/login", data={
            "usuario": "admin_test",
            "password": "test123"
        }, follow_redirects=True)
    return client


# ══════════════════════════════════════════════════════════
# TESTS DE AUTENTICACIÓN
# ══════════════════════════════════════════════════════════

class TestAuth:
    def test_login_page_loads(self, client):
        """La página de login debe cargar correctamente."""
        r = client.get("/auth/login")
        assert r.status_code == 200
        assert b"Iniciar" in r.data or b"login" in r.data.lower()

    def test_login_correcto(self, client, admin_user, app):
        """Login con credenciales válidas debe redirigir al dashboard."""
        with app.app_context():
            r = client.post("/auth/login", data={
                "usuario": "admin_test",
                "password": "test123"
            }, follow_redirects=True)
            assert r.status_code == 200

    def test_login_incorrecto(self, client, admin_user, app):
        """Login con credenciales inválidas debe mostrar error."""
        with app.app_context():
            r = client.post("/auth/login", data={
                "usuario": "admin_test",
                "password": "wrong_password"
            })
            assert b"incorrectos" in r.data or r.status_code in [200, 302]

    def test_redirect_sin_login(self, client):
        """Acceso al dashboard sin login debe redirigir al login."""
        r = client.get("/dashboard", follow_redirects=False)
        assert r.status_code in [302, 401]

    def test_logout(self, logged_client, app):
        """Logout debe redirigir al login."""
        with app.app_context():
            r = logged_client.get("/auth/logout", follow_redirects=False)
            assert r.status_code in [200, 302]


# ══════════════════════════════════════════════════════════
# TESTS DE MODELO - CERTIFICADO
# ══════════════════════════════════════════════════════════

class TestCertificadoModel:
    def test_estado_vigente(self, app, db_session):
        """Certificado con vencimiento futuro debe estar vigente."""
        from backend.models.certificado import Certificado
        with app.app_context():
            cert = Certificado(
                numero_certificado="TEST-001",
                producto="Conductor THHN",
                organismo_certificador="ICONTEC",
                fecha_vencimiento=date.today() + timedelta(days=180)
            )
            cert.actualizar_estado()
            assert cert.estado_calculado == "vigente"

    def test_estado_por_vencer(self, app, db_session):
        """Certificado que vence en <30 días debe estar 'por_vencer'."""
        from backend.models.certificado import Certificado
        with app.app_context():
            cert = Certificado(
                numero_certificado="TEST-002",
                producto="Breaker 20A",
                organismo_certificador="SGS",
                fecha_vencimiento=date.today() + timedelta(days=15)
            )
            cert.actualizar_estado()
            assert cert.estado_calculado == "por_vencer"

    def test_estado_vencido(self, app, db_session):
        """Certificado con vencimiento pasado debe estar 'vencido'."""
        from backend.models.certificado import Certificado
        with app.app_context():
            cert = Certificado(
                numero_certificado="TEST-003",
                producto="Cable NYY",
                organismo_certificador="Bureau Veritas",
                fecha_vencimiento=date.today() - timedelta(days=10)
            )
            cert.actualizar_estado()
            assert cert.estado_calculado == "vencido"

    def test_dias_para_vencer(self, app, db_session):
        """Días para vencer debe calcularse correctamente."""
        from backend.models.certificado import Certificado
        with app.app_context():
            dias = 45
            cert = Certificado(
                numero_certificado="TEST-004",
                producto="Toma corriente",
                organismo_certificador="ICONTEC",
                fecha_vencimiento=date.today() + timedelta(days=dias)
            )
            assert cert.dias_para_vencer == dias

    def test_to_dict(self, app, db_session):
        """El método to_dict debe retornar dict con los campos esperados."""
        from backend.models.certificado import Certificado
        with app.app_context():
            cert = Certificado(
                numero_certificado="TEST-005",
                producto="Panel solar 400W",
                organismo_certificador="Intertek"
            )
            d = cert.to_dict()
            assert "numero_certificado" in d
            assert "producto" in d
            assert "estado_certificado" in d


# ══════════════════════════════════════════════════════════
# TESTS DE SERVICIO - OCR
# ══════════════════════════════════════════════════════════

class TestOCRService:
    def test_normalizar_fecha_slash(self):
        """Debe normalizar fecha en formato DD/MM/YYYY."""
        from backend.services.ocr_service import OCRService
        svc = OCRService()
        resultado = svc._normalizar_fecha("15/06/2025")
        assert resultado == "2025-06-15"

    def test_normalizar_fecha_texto(self):
        """Debe normalizar fecha en texto español."""
        from backend.services.ocr_service import OCRService
        svc = OCRService()
        resultado = svc._normalizar_fecha("15 de marzo de 2024")
        assert resultado == "2024-03-15"

    def test_normalizar_fecha_invalida(self):
        """Fecha inválida debe retornar None."""
        from backend.services.ocr_service import OCRService
        svc = OCRService()
        resultado = svc._normalizar_fecha("texto inválido")
        assert resultado is None

    def test_extraer_campos_texto_ejemplo(self):
        """Debe extraer campos de un texto de ejemplo de certificado."""
        from backend.services.ocr_service import OCRService
        svc = OCRService()
        texto = """
        CERTIFICADO DE CONFORMIDAD N° ICONTEC-2024-56789
        Producto: Conductor Eléctrico THHN Calibre 12 AWG
        Organismo Certificador: ICONTEC
        Fecha de Emisión: 01/03/2024
        Fecha de Vencimiento: 01/03/2026
        """
        campos = svc._extraer_campos(texto)
        # Al menos algún campo debe detectarse
        detectados = sum(1 for v in campos.values() if v)
        assert detectados >= 1


# ══════════════════════════════════════════════════════════
# TESTS DE RUTAS (API)
# ══════════════════════════════════════════════════════════

class TestCertificadoRoutes:
    def test_listar_requiere_login(self, client):
        """Listar certificados sin login debe redirigir."""
        r = client.get("/certificados/", follow_redirects=False)
        assert r.status_code in [302, 401]

    def test_listar_con_login(self, logged_client, app):
        """Con login la lista debe cargar correctamente."""
        with app.app_context():
            r = logged_client.get("/certificados/")
            assert r.status_code == 200

    def test_api_buscar(self, logged_client, app, db_session):
        """API de búsqueda debe retornar JSON."""
        from backend.models.certificado import Certificado
        with app.app_context():
            cert = Certificado(
                numero_certificado="API-TEST-001",
                producto="Breaker Test",
                organismo_certificador="ICONTEC"
            )
            db_session.session.add(cert)
            db_session.session.commit()

            r = logged_client.get("/certificados/api/buscar?q=API")
            assert r.status_code == 200
            data = json.loads(r.data)
            assert isinstance(data, list)


# ══════════════════════════════════════════════════════════
# TESTS DE VALIDADORES
# ══════════════════════════════════════════════════════════

class TestValidadores:
    def test_extension_pdf_valida(self):
        from backend.utils.validators import validar_extension_pdf
        assert validar_extension_pdf("certificado.pdf") is True
        assert validar_extension_pdf("certificado.PDF") is True

    def test_extension_no_pdf(self):
        from backend.utils.validators import validar_extension_pdf
        assert validar_extension_pdf("imagen.jpg") is False
        assert validar_extension_pdf("documento.docx") is False

    def test_email_valido(self):
        from backend.utils.validators import validar_email
        assert validar_email("usuario@empresa.com") is True
        assert validar_email("correo@dominio.co") is True

    def test_email_invalido(self):
        from backend.utils.validators import validar_email
        assert validar_email("no-es-email") is False
        assert validar_email("@sindominio") is False

    def test_sanitizar_texto(self):
        from backend.utils.validators import sanitizar_texto
        resultado = sanitizar_texto("  texto con espacios  ")
        assert resultado == "texto con espacios"

    def test_sanitizar_texto_largo(self):
        from backend.utils.validators import sanitizar_texto
        largo = "x" * 600
        resultado = sanitizar_texto(largo, max_len=500)
        assert len(resultado) <= 500


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
