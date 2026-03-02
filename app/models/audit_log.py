import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class AuditAction(str, enum.Enum):
    # ── Auth ─────────────────────────────────────
    USER_REGISTERED = "USER_REGISTERED"
    USER_LOGIN = "USER_LOGIN"
    USER_LOGIN_FAILED = "USER_LOGIN_FAILED"
    USER_LOGOUT = "USER_LOGOUT"
    TOKEN_REFRESHED = "TOKEN_REFRESHED"
    TOKEN_REVOKED = "TOKEN_REVOKED"

    # ── User ─────────────────────────────────────
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_BALANCE_ADDED = "USER_BALANCE_ADDED"
    USER_BALANCE_SUBTRACTED = "USER_BALANCE_SUBTRACTED"

    # ── Transactions ─────────────────────────────
    DEPOSIT_CREATED = "DEPOSIT_CREATED"
    DEPOSIT_FAILED = "DEPOSIT_FAILED"
    WITHDRAWAL_CREATED = "WITHDRAWAL_CREATED"
    WITHDRAWAL_FAILED = "WITHDRAWAL_FAILED"
    TRANSFER_CREATED = "TRANSFER_CREATED"
    TRANSFER_FAILED = "TRANSFER_FAILED"


class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'

    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction),
        nullable=False
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id'),
        nullable=True
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=True
    )

    details: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f'<AuditLog {self.action.value} by {self.user_id} at {self.created_at}>'
