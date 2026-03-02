import logging
import sys
from http import HTTPStatus
from uuid import UUID

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

from app.config import JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES, JWT_REFRESH_TOKEN_EXPIRES, SQLALCHEMY_DATABASE_URI, \
    SECRET_KEY
from app.extensions import db, jwt
from app.utils.response_factory import response_error


def _configure_logging(app: Flask) -> None:
    """Configura el sistema de logging de la aplicación."""
    log_format = (
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    formatter = logging.Formatter(log_format)

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Handler para archivo
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Configurar logger raíz de la app
    app.logger.handlers.clear()
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

    # Configurar logger del módulo de auditoría
    audit_logger = logging.getLogger("app.services.audit_service")
    audit_logger.handlers.clear()
    audit_logger.addHandler(console_handler)
    audit_logger.addHandler(file_handler)
    audit_logger.setLevel(logging.INFO)


def create_app():
    app = Flask(__name__)

    # ── Configuración de base de datos ───────────────────
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ── Configuración JWT ────────────────────────────────
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWT_ACCESS_TOKEN_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = JWT_REFRESH_TOKEN_EXPIRES

    app.secret_key = SECRET_KEY

    # ── Inicializar extensiones ──────────────────────────
    db.init_app(app)
    jwt.init_app(app)

    # ── Verificación de tokens revocados
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from app.repositories.revoked_token_repository import RevokedTokenRepository
        jti = jwt_payload.get("jti")
        if not jti:
            return False
        repo = RevokedTokenRepository()
        return repo.is_revoked(UUID(jti))

    # ── Configurar logging ───────────────────────────────
    _configure_logging(app)

    from app.models import User, Transaction, TransactionType, AuditLog, RevokedToken

    with app.app_context():
        db.create_all()

    # ── Registrar blueprints ─────────────────────────────
    from app.routes.auth import bp as auth_bp
    from app.routes.users import bp as users_bp
    from app.routes.transactions import bp as transactions_bp
    from app.routes.audit import bp as audit_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(audit_bp)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/login")
    def login_page():
        return render_template("auth/login.html")

    @app.get("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    from app.common.exceptions.domain_exceptions import (
        DomainException,
        ResourceNotFoundException,
        ResourceAlreadyExistsException,
        InvalidOperationException,
        UnauthorizedException,
        ForbiddenException,
    )

    exception_status_map: dict[type[DomainException], HTTPStatus] = {
        ResourceNotFoundException: HTTPStatus.NOT_FOUND,
        ResourceAlreadyExistsException: HTTPStatus.CONFLICT,
        InvalidOperationException: HTTPStatus.BAD_REQUEST,
        UnauthorizedException: HTTPStatus.UNAUTHORIZED,
        ForbiddenException: HTTPStatus.FORBIDDEN,
    }

    @app.errorhandler(DomainException)
    def handle_domain_exception(e: DomainException):
        cls = e.__class__
        status = exception_status_map.get(cls, HTTPStatus.BAD_REQUEST)
        app.logger.warning(f"DomainException: {cls.__name__} - {e.message}")
        return response_error(
            message=e.message,
            status=status
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        app.logger.warning(f"HTTPException: {e.code} - {e.description}")
        return response_error(
            message=e.description,
            status=HTTPStatus(e.code)
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(e: Exception):
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        return response_error(
            message="Ocurrió un error inesperado.",
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

    # ── Manejo de errores JWT ────────────────────────────
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return response_error(
            message="El token ha expirado.",
            status=HTTPStatus.UNAUTHORIZED
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return response_error(
            message="Token inválido.",
            status=HTTPStatus.UNAUTHORIZED
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return response_error(
            message="Token de autorización requerido.",
            status=HTTPStatus.UNAUTHORIZED
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return response_error(
            message="El token ha sido revocado.",
            status=HTTPStatus.UNAUTHORIZED
        )

    return app
