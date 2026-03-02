from uuid import UUID

from flask_jwt_extended import create_access_token, create_refresh_token

from app.common.exceptions.domain_exceptions import UnauthorizedException
from app.common.security import verify_password
from app.contracts.user import LoginResult
from app.models import AuditAction
from app.models import TokenType
from app.repositories import RevokedTokenRepository
from app.services.audit_service import AuditService
from app.services.user_service import UserService


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        audit_service: AuditService,
        revoked_token_repository: RevokedTokenRepository,
    ):
        self.user_service = user_service
        self.audit_service = audit_service
        self.revoked_token_repo = revoked_token_repository

    def authenticate(self, email: str, password: str) -> LoginResult:
        user_data = self.user_service.find_for_authentication(email)

        if not user_data or not verify_password(password, user_data.hashed_password):
            self.audit_service.log(
                AuditAction.USER_LOGIN_FAILED,
                details={"email": email, "reason": "Credenciales inválidas"}
            )
            raise UnauthorizedException("Credenciales inválidas.")

        # Generar tokens JWT
        identity = str(user_data.user_id)
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        self.audit_service.log(
            AuditAction.USER_LOGIN,
            user_id=user_data.user_id,
            details={"email": email}
        )

        user_summary = self.user_service.get_user_by_id(user_data.user_id)

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_summary
        )

    def refresh_access_token(self, user_id: UUID, refresh_jti: UUID) -> dict:
        self.revoked_token_repo.add(jti=refresh_jti, token_type=TokenType.REFRESH)

        access_token = create_access_token(identity=str(user_id))

        self.audit_service.log(
            AuditAction.TOKEN_REFRESHED,
            user_id=user_id,
            details={"action": "Token de acceso renovado", "refresh_jti_revoked": refresh_jti}
        )

        return {"access_token": access_token}

    def logout(self, user_id: UUID, access_jti: UUID, refresh_jti: UUID | None = None) -> None:
        self.revoked_token_repo.add(jti=access_jti, token_type=TokenType.ACCESS)

        if refresh_jti:
            self.revoked_token_repo.add(jti=refresh_jti, token_type=TokenType.REFRESH)

        self.audit_service.log(
            AuditAction.USER_LOGOUT,
            user_id=user_id,
            details={"action": "Sesión cerrada", "access_jti_revoked": access_jti}
        )

