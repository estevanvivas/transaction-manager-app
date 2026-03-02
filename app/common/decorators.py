from functools import wraps
from http import HTTPStatus

from flask import request, jsonify
from marshmallow import ValidationError

from app import response_error


def validate_schema(schema_cls):
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return response_error(
                    message="La solicitud debe contener JSON.",
                    status=HTTPStatus.BAD_REQUEST
                )

            try:
                schema = schema_cls()
                data = schema.load(request.get_json())
            except ValidationError as err:
                return response_error(
                    message="Error de validación.",
                    errors=err.messages,
                    status=HTTPStatus.UNPROCESSABLE_ENTITY
                )

            return func(data, *args, **kwargs)

        return wrapper

    return decorator
