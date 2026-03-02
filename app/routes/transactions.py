from http import HTTPStatus
from uuid import UUID

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.common.decorators import validate_schema
from app.repositories import TransactionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.transactions_schemas import DepositSchema, TransferSchema, WithdrawalSchema
from app.services.audit_service import AuditService
from app.services.transaction_service import TransactionService
from app.services.user_service import UserService
from app.utils.response_factory import response_success

bp = Blueprint("transactions", __name__, url_prefix="/transactions")

_audit_service = AuditService(AuditLogRepository())
_user_service = UserService(UserRepository())
_transaction_service = TransactionService(TransactionRepository(), _user_service, _audit_service)


@bp.post("/deposit")
@jwt_required()
@validate_schema(DepositSchema)
def deposit_transaction(data):
    user_id = UUID(get_jwt_identity())
    deposit_details = _transaction_service.create_deposit(
        user_id=user_id,
        amount=data["amount"]
    )

    return response_success(
        status=HTTPStatus.CREATED,
        data=deposit_details,
        message="Depósito realizado exitosamente",
    )


@bp.post("/withdrawal")
@jwt_required()
@validate_schema(WithdrawalSchema)
def withdraw_transaction(data):
    user_id = UUID(get_jwt_identity())
    withdrawal_details = _transaction_service.create_withdrawal(
        user_id=user_id,
        amount=data["amount"]
    )

    return response_success(
        status=HTTPStatus.CREATED,
        data=withdrawal_details,
        message="Retiro realizado exitosamente",
    )


@bp.post("/transfer")
@jwt_required()
@validate_schema(TransferSchema)
def transfer_transaction(data):
    sender_id = UUID(get_jwt_identity())
    transfer_details = _transaction_service.create_transfer(
        sender_id=sender_id,
        target_username=data["recipient_username"],
        amount=data["amount"]
    )

    return response_success(
        status=HTTPStatus.CREATED,
        data=transfer_details,
        message="Transferencia realizada exitosamente",
    )


@bp.get("/")
@jwt_required()
def get_transactions():
    user_id = UUID(get_jwt_identity())
    transactions = _transaction_service.get_user_transactions(user_id)

    return response_success(
        status=HTTPStatus.OK,
        data=transactions,
        message="Transacciones obtenidas exitosamente.",
    )
