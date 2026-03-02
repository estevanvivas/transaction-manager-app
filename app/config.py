import os
from datetime import timedelta
from decimal import Decimal

from dotenv import load_dotenv

from app.models import TransactionType

load_dotenv()


# ── Comisiones por tipo de transacción ───────────────────────
# Expresadas como porcentaje (ej: 0.01 = 1%)
COMMISSION_RATES: dict[TransactionType, Decimal] = {
    TransactionType.DEPOSIT: Decimal('0.00'),       # 0% - sin comisión
    TransactionType.WITHDRAWAL: Decimal('0.02'),     # 2%
    TransactionType.TRANSFER: Decimal('0.03'),       # 3%
}


def get_commission_rate(transaction_type: TransactionType) -> Decimal:
    """Obtiene la tasa de comisión para un tipo de transacción."""
    return COMMISSION_RATES.get(transaction_type, Decimal('0.00'))


def calculate_commission(transaction_type: TransactionType, amount: Decimal) -> Decimal:
    """Calcula el monto de la comisión para un tipo de transacción y monto dado."""
    rate = get_commission_rate(transaction_type)
    return (amount * rate).quantize(Decimal('0.01'))


# ── Configuración de la aplicación ───────────────────────────
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")

# ── Configuración JWT ────────────────────────────────────────
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-super-secret-key-change-in-production")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "1")))
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "30")))

