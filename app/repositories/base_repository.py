from typing import TypeVar, Generic, List, Optional, Type
from uuid import UUID

from sqlalchemy.orm import Session

from app.extensions import db
from app.models.base import BaseModel

T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T]):

    def __init__(self, model: Type[T]):
        self.model = model
        self.session: Session = db.session

    def get_by_id(self, id: UUID) -> Optional[T]:
        return self.session.get(self.model, id)

    def get_all(self) -> List[T]:
        """Obtener todas las entidades"""
        return self.session.query(self.model).all()

    def create(self, entity: T) -> T:
        """Crear nueva entidad"""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update(self, entity: T) -> T:
        """Actualizar entidad existente"""
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: T) -> None:
        """Eliminar entidad"""
        self.session.delete(entity)
        self.session.commit()

    def delete_by_id(self, id: UUID) -> bool:
        """Eliminar entidad por ID"""
        entity = self.get_by_id(id)
        if entity:
            self.delete(entity)
            return True
        return False

    def count(self) -> int:
        """Contar todas las entidades"""
        return self.session.query(self.model).count()

    def exists_by_id(self, id: UUID) -> bool:
        """Verificar si existe una entidad por ID"""
        return self.get_by_id(id) is not None
