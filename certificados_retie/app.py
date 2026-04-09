"""
==============================================================
Sistema de Gestión de Certificados RETIE
app.py - Punto de entrada principal de la aplicación
==============================================================
"""

import os
from flask import Flask
from backend.database import db, init_db
from backend.models.user import User
from backend.models.certificado import Certificado
from backend.routes.auth_routes import auth_bp
from backend.routes.certificado_routes import cert_bp
from backend.routes.dashboard_routes import dashboard_bp
from backend.routes.report_routes import report_bp
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

def create_app(config_name="development"):
    """Factory de aplicación Flask."""
    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static"
    )

    # ── Configuración ──────────────────────────────────────
    from backend.config import config_map
    app.config.from_object(config_map[config_name])

    # ── Inicializar extensiones ────────────────────────────
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor inicia sesión para continuar."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Blueprints ─────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(cert_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(report_bp)

    # ── Crear tablas y usuario admin inicial ───────────────
    with app.app_context():
        db.create_all()
        init_db(app)

    return app


if __name__ == "__main__":
    app = create_app(os.getenv("FLASK_ENV", "development"))
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print(f"\n{'='*55}")
    print(f"  Sistema RETIE iniciado")
    print(f"  Acceso local:  http://localhost:{port}")
    print(f"  Red local:     http://<IP-DEL-SERVIDOR>:{port}")
    print(f"{'='*55}\n")
    app.run(host=host, port=port, debug=debug)
