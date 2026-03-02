from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload

from app.models.transaction import Transaction
from app.repositories.base_repository import BaseRepository


class TransactionRepository(BaseRepository):
    """Repositorio para operaciones específicas de Transaction"""

    def __init__(self):
        super().__init__(Transaction)

    def get_by_user_id(self, user_id: UUID) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .options(
                joinedload(Transaction.user),
                joinedload(Transaction.target_user)
            )
            .where(
                or_(
                    Transaction.user_id == user_id,
                    Transaction.target_user_id == user_id
                )
            )
        )
        return list(self.session.execute(stmt).scalars().all())
