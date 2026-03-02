from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class TransactionDetails:
    amount: Decimal
    commission: Decimal
    timestamp: datetime
    status: str
    type: str = field(default='', init=False)


@dataclass
class DepositDetails(TransactionDetails):
    type: str = field(default='deposit', init=False)


@dataclass
class WithdrawalDetails(TransactionDetails):
    type: str = field(default='withdrawal', init=False)


@dataclass
class TransferSendDetails(TransactionDetails):
    recipient_username: str = ''
    type: str = field(default='transfer_send', init=False)


@dataclass
class TransferReceiveDetails(TransactionDetails):
    sender_username: str = ''
    type: str = field(default='transfer_receive', init=False)
