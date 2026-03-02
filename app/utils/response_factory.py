from http import HTTPStatus

from flask import jsonify


def response_success(*, data=None, message: str = "Operación exitosa", status: HTTPStatus = HTTPStatus.OK):
    payload = {
        "status": status.name,
        "message": message,
    }

    if data is not None:
        payload["data"] = data

    return jsonify(payload), status.value


def response_error(*, message: str = "Ocurrió un error", errors=None, status: HTTPStatus = HTTPStatus.BAD_REQUEST):
    payload = {
        "status": status.name,
        "message": message,
    }

    if errors is not None:
        payload["errors"] = errors

    return jsonify(payload), status.value
