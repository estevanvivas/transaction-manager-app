import json
import logging
from uuid import UUID

from flask import request

from app.models import AuditAction
from app.models import AuditLog
from app.repositories import AuditLogRepository

logger = logging.getLogger(__name__)


class AuditService:
    """Servicio para registrar eventos de auditoría en la base de datos y en logs del sistema."""

    def __init__(self, audit_log_repository: AuditLogRepository):
        self.audit_log_repository = audit_log_repository

    def log(
            self,
            action: AuditAction,
            *,
            user_id: UUID | None = None,
            details: dict | None = None,
    ) -> AuditLog:
        """Registra un evento de auditoría."""
        ip_address = self._get_client_ip()
        details_str = json.dumps(details, default=str) if details else None

        audit_log = AuditLog(
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            details=details_str,
        )

        created_log = self.audit_log_repository.create(audit_log)

        # También registramos en el log del sistema
        log_message = (
            f"[AUDIT] action={action.value} "
            f"user_id={user_id} "
            f"ip={ip_address} "
            f"details={details_str}"
        )
        logger.info(log_message)

        return created_log

    def get_user_logs(self, user_id: UUID, limit: int = 50) -> list[AuditLog]:
        """Obtiene los logs de auditoría de un usuario."""
        return self.audit_log_repository.get_by_user_id(user_id, limit)

    def get_recent_logs(self, limit: int = 100) -> list[AuditLog]:
        """Obtiene los logs más recientes."""
        return self.audit_log_repository.get_recent(limit)

    @staticmethod
    def _get_client_ip() -> str | None:
        """Obtiene la IP del cliente de la solicitud actual."""
        try:
            if request.headers.get('X-Forwarded-For'):
                return request.headers['X-Forwarded-For'].split(',')[0].strip()
            return request.remote_addr
        except RuntimeError:
            # Fuera de contexto de request
            return None

