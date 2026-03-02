import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import mapped_column, Mapped

from app.extensions import db


class BaseModel(db.Model):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
