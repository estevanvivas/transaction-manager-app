from decimal import Decimal
from uuid import UUID

from app.common.exceptions.domain_exceptions import (
    ResourceNotFoundException,
    ResourceAlreadyExistsException, InvalidOperationException,
)
from app.common.security import hash_password
from app.contracts.user import UserSummary, UserContext, UserDetails
from app.models.user import User
from app.repositories import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def _get_user_or_raise(self, user_id: UUID) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("Usuario no encontrado.")
        return user

    def get_id_by_username(self, username: str) -> UUID:
        user = self.user_repository.find_by_username(username)
        if not user:
            raise ResourceNotFoundException("Usuario no encontrado.")
        return user.id

    def get_user_by_id(self, user_id: UUID) -> UserSummary:
        return self._to_summary(self._get_user_or_raise(user_id))

    def create_user(self, *, username: str, email: str, password: str) -> UserSummary:
        self._check_unique_email(email)
        self._check_unique_username(username)

        hashed_password = hash_password(password)

        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
        )

        created_user = self.user_repository.create(new_user)

        return self._to_summary(created_user)

    def get_user_balance(self, user_id: UUID) -> Decimal:
        user = self._get_user_or_raise(user_id)
        return user.balance

    def get_user_details_by_username(self, username: str) -> UserDetails:
        user = self.user_repository.find_by_username(username)
        if not user:
            raise ResourceNotFoundException("Usuario no encontrado.")
        return self._to_details(user)

    def find_for_authentication(self, email) -> UserContext | None:
        user = self.user_repository.find_by_email(email)
        if not user:
            return None

        return UserContext(
            user_id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password
        )

    def _check_unique_email(self, email: str) -> None:
        """Verifica que el email no esté registrado."""
        if self.user_repository.exists_by_email(email):
            raise ResourceAlreadyExistsException("Ya existe una cuenta con ese correo electrónico.")

    def _check_unique_username(self, username: str) -> None:
        if self.user_repository.exists_by_username(username):
            raise ResourceAlreadyExistsException("El nombre de usuario ya está en uso.")

    def update_user(self, user_id: UUID, username: str = None, email: str = None) -> UserSummary:
        user = self._get_user_or_raise(user_id)

        if username and username != user.username:
            self._check_unique_username(username)
            user.username = username

        if email and email != user.email:
            self._check_unique_email(email)
            user.email = email

        updated_user = self.user_repository.update(user)
        return self._to_summary(updated_user)

    def delete_user(self, user_id: UUID) -> None:
        user = self._get_user_or_raise(user_id)
        self.user_repository.delete(user)

    def add_balance(self, user_id: UUID, amount: Decimal) -> None:
        user = self._get_user_or_raise(user_id)
        user.balance += amount
        self.user_repository.update(user)

    def subtract_balance(self, user_id: UUID, amount: Decimal) -> None:
        user = self._get_user_or_raise(user_id)
        if user.balance < amount:
            raise InvalidOperationException("Saldo insuficiente.")
        user.balance -= amount
        self.user_repository.update(user)

    def _to_summary(self, user: User) -> UserSummary:
        return UserSummary(
            username=user.username,
            email=user.email,
            balance=user.balance
        )

    def _to_details(self, user: User) -> UserDetails:
        return UserDetails(
            id=user.id,
            username=user.username,
            email=user.email,
            balance=user.balance
        )
