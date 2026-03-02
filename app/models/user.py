from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Numeric, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00')
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __init__(
            self,
            *,
            username: str,
            email: str,
            hashed_password: str,
    ) -> None:
        self.username = username
        self.email = email
        self.hashed_password = hashed_password

    def __repr__(self):
        return f'<User {self.email}>'
