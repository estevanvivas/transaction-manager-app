from marshmallow import Schema, fields, validate

from app.schemas.user_schemas import username_field


class TransactionBaseSchema(Schema):
    amount = fields.Decimal(
        required=True,
        validate=validate.Range(min=0, error="El monto debe ser un número positivo."),
        error_messages={
            "required": "El monto es obligatorio.",
            "invalid": "El monto debe ser un número decimal válido.",
            "special": "El monto no es válido."
        }
    )


class DepositSchema(TransactionBaseSchema):
    pass


class WithdrawalSchema(TransactionBaseSchema):
    pass


class TransferSchema(TransactionBaseSchema):
    recipient_username = username_field
