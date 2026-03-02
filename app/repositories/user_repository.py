from typing import Optional

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Repositorio para operaciones específicas de User"""

    def __init__(self):
        super().__init__(User)

    def find_by_email(self, email: str) -> Optional[User]:
        """Buscar usuario por email"""
        return self.session.query(User).filter_by(email=email).first()

    def find_by_username(self, username: str) -> Optional[User]:
        """Buscar usuario por username"""
        return self.session.query(User).filter_by(username=username).first()

    def exists_by_email(self, email: str) -> bool:
        """Verificar si existe un usuario con el email dado"""
        return self.find_by_email(email) is not None

    def exists_by_username(self, username: str) -> bool:
        """Verificar si existe un usuario con el username dado"""
        return self.find_by_username(username) is not None
