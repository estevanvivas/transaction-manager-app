from http import HTTPStatus
from uuid import UUID

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.repositories import UserRepository
from app.services.user_service import UserService
from app.utils.response_factory import response_success

bp = Blueprint('users', __name__, url_prefix='/users')

_user_service = UserService(UserRepository())


@bp.get('/me')
@jwt_required()
def get_current_user():
    user_id = UUID(get_jwt_identity())
    user = _user_service.get_user_by_id(user_id)
    return response_success(
        status=HTTPStatus.OK,
        message="Usuario obtenido exitosamente.",
        data=user
    )
