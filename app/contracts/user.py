from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class UserSummary:
    username: str
    email: str
    balance: Decimal

@dataclass
class UserDetails:
    id: UUID
    username: str
    email: str
    balance: Decimal


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str
    user: UserSummary


@dataclass
class UserContext:
    user_id: UUID
    username: str
    email: str
    hashed_password: str
