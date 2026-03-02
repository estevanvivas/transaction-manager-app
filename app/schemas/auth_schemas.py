import re

from marshmallow import Schema, fields, validate

from app.schemas.user_schemas import username_field, email_field

SPECIAL_CHARS = "!@#$%^&*()_+-=[]{};':\"\\|,.<>/?"

password_field = fields.String(
    required=True,
    validate=[
        validate.Length(min=8, error="La contraseña debe tener al menos {min} caracteres."),
        validate.Length(max=100, error="La contraseña es demasiado larga."),
        validate.Regexp(r".*[A-Z]", error="Debe contener una mayúscula."),
        validate.Regexp(r".*[a-z]", error="Debe contener una minúscula."),
        validate.Regexp(r".*\d", error="Debe contener un número."),
        validate.Regexp(
            regex=rf".*[{re.escape(SPECIAL_CHARS)}]",
            error=f"Debe contener al menos un carácter especial."
        ),
    ],
    error_messages={
        "required": "La contraseña es obligatoria.",
        "null": "La contraseña no puede ser nula.",
        "invalid": "La contraseña debe ser una cadena de texto.",
    },
)


class UserRegistrationSchema(Schema):
    username = username_field
    email = email_field
    password = password_field


class LoginSchema(Schema):
    email = fields.Email(
        required=True,
        error_messages={
            "required": "El correo electrónico es obligatorio.",
            "null": "El correo electrónico no puede ser nulo.",
            "invalid": "El correo electrónico no tiene un formato válido.",
        },
    )

    password = fields.String(
        required=True,
        load_only=True,
        error_messages={
            "required": "La contraseña es obligatoria.",
            "null": "La contraseña no puede ser nula.",
            "invalid": "La contraseña debe ser una cadena de texto.",
        },
    )
