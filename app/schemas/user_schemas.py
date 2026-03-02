from marshmallow import fields, validate

username_field = fields.String(
    required=True,
    validate=[
        validate.Length(min=3, error="El nombre de usuario debe tener al menos {min} caracteres."),
        validate.Length(max=10, error="El nombre de usuario no puede tener más de {max} caracteres."),
        validate.Regexp(r"^[a-zA-Z0-9_]+$",
                        error="El nombre de usuario solo puede contener letras, números y guiones bajos."),
    ],
    error_messages={
        "required": "El nombre de usuario es obligatorio.",
        "null": "El nombre de usuario no puede ser nulo.",
        "invalid": "El nombre de usuario debe ser una cadena de texto.",
    },
)

email_field = fields.Email(
    required=True,
    validate=validate.Length(max=100, error="El correo electrónico es demasiado largo."),
    error_messages={
        "required": "El correo electrónico es obligatorio.",
        "null": "El correo electrónico no puede ser nulo.",
        "invalid": "El correo electrónico no tiene un formato válido.",
    },
)
