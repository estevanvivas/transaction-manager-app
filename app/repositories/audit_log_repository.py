from uuid import UUID

from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.repositories.base_repository import BaseRepository


class AuditLogRepository(BaseRepository):
    """Repositorio para operaciones de AuditLog."""

    def __init__(self):
        super().__init__(AuditLog)

    def get_by_user_id(self, user_id: UUID, limit: int = 50) -> list[AuditLog]:
        """Obtiene los logs de auditoría de un usuario."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_recent(self, limit: int = 100) -> list[AuditLog]:
        """Obtiene los logs de auditoría más recientes."""
        stmt = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

