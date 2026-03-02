import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class TransactionStatus(str, enum.Enum):
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class TransactionType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"


class Transaction(BaseModel):
    __tablename__ = 'transactions'

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    commission: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal('0.00')
    )

    transaction_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType),
        nullable=False
    )

    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus),
        nullable=False
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id'),
        nullable=False
    )

    target_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id'),
        nullable=True
    )

    user: Mapped['User'] = relationship(
        'User',
        foreign_keys=[user_id],
        lazy='select'
    )

    target_user: Mapped['User'] = relationship(
        'User',
        foreign_keys=[target_user_id],
        lazy='select'
    )

    @property
    def total_cost(self) -> Decimal:
        """Monto total incluyendo comisión (para retiros y transferencias)."""
        return self.amount + self.commission

    def __repr__(self):
        return f'<Transaction {self.type.value} {self.amount} (commission: {self.commission}) on {self.transaction_date}>'
