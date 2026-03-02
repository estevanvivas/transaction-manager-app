import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func, Enum as SAEnum, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class TokenType(str, enum.Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class RevokedToken(BaseModel):
    __tablename__ = 'revoked_tokens'

    jti: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        index=True
    )

    token_type: Mapped[TokenType] = mapped_column(
        SAEnum(TokenType),
        nullable=False
    )

    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    def __init__(self, *, jti: UUID, token_type: TokenType) -> None:
        self.jti = jti
        self.token_type = token_type

    def __repr__(self) -> str:
        return f'<RevokedToken jti={self.jti} type={self.token_type}>'

