from http import HTTPStatus
from uuid import UUID

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.common.decorators import validate_schema
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.revoked_token_repository import RevokedTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas import LoginSchema
from app.schemas.auth_schemas import UserRegistrationSchema
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.response_factory import response_success

bp = Blueprint("auth", __name__, url_prefix="/auth")

_audit_service = AuditService(AuditLogRepository())
_user_service = UserService(UserRepository())
_revoked_token_repo = RevokedTokenRepository()
_auth_service = AuthService(_user_service, _audit_service, _revoked_token_repo)


@bp.post("/register")
@validate_schema(UserRegistrationSchema)
def register_user(user_data):
    created_user = _user_service.create_user(**user_data)

    return response_success(
        data=created_user,
        message="Usuario registrado exitosamente",
        status=HTTPStatus.CREATED
    )


@bp.post("/login")
@validate_schema(LoginSchema)
def login(credentials):
    login_result = _auth_service.authenticate(**credentials)
    return response_success(
        data=login_result,
        message="Inicio de sesión exitoso",
        status=HTTPStatus.OK
    )


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = UUID(get_jwt_identity())
    refresh_jti = get_jwt()["jti"]
    tokens = _auth_service.refresh_access_token(current_user_id, UUID(refresh_jti))
    return response_success(
        data=tokens,
        message="Token renovado exitosamente",
        status=HTTPStatus.OK
    )


@bp.post("/logout")
@jwt_required()
def logout():
    jwt_data = get_jwt()
    access_jti = jwt_data["jti"]
    current_user_id = UUID(get_jwt_identity())

    _auth_service.logout(user_id=current_user_id, access_jti=UUID(access_jti))

    return response_success(
        data=None,
        message="Sesión cerrada exitosamente",
        status=HTTPStatus.OK
    )


@bp.post("/logout/refresh")
@jwt_required(refresh=True)
def logout_refresh():
    jwt_data = get_jwt()
    refresh_jti = jwt_data["jti"]
    current_user_id = UUID(get_jwt_identity())

    _auth_service.logout(user_id=current_user_id, access_jti=UUID(refresh_jti))

    return response_success(
        data=None,
        message="Refresh token revocado exitosamente",
        status=HTTPStatus.OK
    )

