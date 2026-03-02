from uuid import UUID

from marshmallow.fields import Decimal

from app.common.exceptions.domain_exceptions import InvalidOperationException
from app.config import calculate_commission
from app.contracts.transaction import TransactionDetails, DepositDetails, WithdrawalDetails, TransferSendDetails, \
    TransferReceiveDetails
from app.models import Transaction, TransactionType
from app.models import AuditAction
from app.models import TransactionStatus
from app.services.audit_service import AuditService


class TransactionService:
    def __init__(self, transaction_repository, user_service, audit_service: AuditService):
        self.transaction_repository = transaction_repository
        self.user_service = user_service
        self.audit_service = audit_service

    def create_deposit(self, *, user_id: UUID, amount: Decimal) -> TransactionDetails:
        commission = calculate_commission(TransactionType.DEPOSIT, amount)

        deposit = Transaction(
            user_id=user_id,
            amount=amount,
            commission=commission,
            type=TransactionType.DEPOSIT,
            status=TransactionStatus.COMPLETED
        )
        transaction_created = self.transaction_repository.create(deposit)

        # En depósito, el usuario recibe el monto neto (amount - comisión)
        net_amount = amount - commission
        self.user_service.add_balance(user_id, net_amount)

        self.audit_service.log(
            AuditAction.DEPOSIT_CREATED,
            user_id=user_id,
            details={
                "transaction_id": str(transaction_created.id),
                "amount": str(amount),
                "commission": str(commission),
                "net_amount": str(net_amount),
            }
        )

        return self._to_dto(transaction_created, user_id)

    def create_withdrawal(self, *, user_id: UUID, amount: Decimal) -> TransactionDetails:
        commission = calculate_commission(TransactionType.WITHDRAWAL, amount)
        total_required = amount + commission

        try:
            self.user_service.subtract_balance(user_id, total_required)
            status = TransactionStatus.COMPLETED
        except InvalidOperationException:
            status = TransactionStatus.FAILED

        withdrawal = Transaction(
            user_id=user_id,
            amount=amount,
            commission=commission,
            type=TransactionType.WITHDRAWAL,
            status=status
        )
        transaction = self.transaction_repository.create(withdrawal)

        if status == TransactionStatus.FAILED:
            self.audit_service.log(
                AuditAction.WITHDRAWAL_FAILED,
                user_id=user_id,
                details={
                    "transaction_id": str(transaction.id),
                    "amount": str(amount),
                    "commission": str(commission),
                    "total_required": str(total_required),
                    "reason": "Fondos insuficientes",
                }
            )
            raise InvalidOperationException(
                f"Fondos insuficientes para realizar el retiro. "
                f"Se requiere {total_required} (monto: {amount} + comisión: {commission})."
            )

        self.audit_service.log(
            AuditAction.WITHDRAWAL_CREATED,
            user_id=user_id,
            details={
                "transaction_id": str(transaction.id),
                "amount": str(amount),
                "commission": str(commission),
                "total_deducted": str(total_required),
            }
        )

        return self._to_dto(transaction, user_id)

    def create_transfer(self, *, sender_id: UUID, target_username: str, amount: Decimal) -> TransactionDetails:
        target_user = self.user_service.get_user_details_by_username(target_username)
        recipient_id = target_user.id
        if sender_id == recipient_id:
            raise InvalidOperationException(
                "Transferencia inválida: el remitente y el destinatario no pueden ser el mismo usuario.")

        commission = calculate_commission(TransactionType.TRANSFER, amount)
        total_required = amount + commission

        try:
            self.user_service.subtract_balance(sender_id, total_required)
            self.user_service.add_balance(recipient_id, amount)
            status = TransactionStatus.COMPLETED
        except InvalidOperationException:
            status = TransactionStatus.FAILED

        transfer = Transaction(
            user_id=sender_id,
            target_user_id=recipient_id,
            amount=amount,
            commission=commission,
            type=TransactionType.TRANSFER,
            status=status
        )

        transaction = self.transaction_repository.create(transfer)

        if status == TransactionStatus.FAILED:
            self.audit_service.log(
                AuditAction.TRANSFER_FAILED,
                user_id=sender_id,
                details={
                    "transaction_id": str(transaction.id),
                    "recipient_id": str(recipient_id),
                    "amount": str(amount),
                    "commission": str(commission),
                    "total_required": str(total_required),
                    "reason": "Fondos insuficientes",
                }
            )
            raise InvalidOperationException(
                f"Fondos insuficientes para realizar la transferencia. "
                f"Se requiere {total_required} (monto: {amount} + comisión: {commission})."
            )

        self.audit_service.log(
            AuditAction.TRANSFER_CREATED,
            user_id=sender_id,
            details={
                "transaction_id": str(transaction.id),
                "recipient_id": str(recipient_id),
                "amount": str(amount),
                "commission": str(commission),
                "total_deducted": str(total_required),
            }
        )

        return self._to_dto(transaction, sender_id)

    def get_transaction_by_id(self, transaction_id: str):
        """Obtiene una transacción por su ID."""
        transaction = self.transaction_repository.get_by_id(transaction_id)
        return transaction

    def get_user_transactions(self, user_id: UUID) -> list[TransactionDetails]:
        transactions = self.transaction_repository.get_by_user_id(user_id)
        return [self._to_dto(t, user_id) for t in transactions]

    def _to_dto(self, transaction: Transaction, user_id: UUID) -> TransactionDetails:
        base = dict(
            amount=transaction.amount,
            commission=transaction.commission,
            timestamp=transaction.transaction_date,
            status=transaction.status.value,
        )

        match transaction.type:
            case TransactionType.DEPOSIT:
                return DepositDetails(**base)

            case TransactionType.WITHDRAWAL:
                return WithdrawalDetails(**base)

            case TransactionType.TRANSFER:
                if transaction.user_id == user_id:
                    return TransferSendDetails(**base, recipient_username=transaction.target_user.username)
                else:
                    return TransferReceiveDetails(**base, sender_username=transaction.user.username)
            case _:
                raise ValueError(f"Tipo de transacción no soportado: {transaction.type}")
