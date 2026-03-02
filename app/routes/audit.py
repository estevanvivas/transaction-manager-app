import json
from http import HTTPStatus
from uuid import UUID

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.repositories.audit_log_repository import AuditLogRepository
from app.services.audit_service import AuditService
from app.utils.response_factory import response_success

bp = Blueprint('audit', __name__, url_prefix='/audit')

_audit_service = AuditService(AuditLogRepository())


@bp.get('/my-logs')
@jwt_required()
def get_my_audit_logs():
    """Obtiene los logs de auditoría del usuario autenticado."""
    user_id = UUID(get_jwt_identity())
    logs = _audit_service.get_user_logs(user_id)

    data = [
        {
            "id": str(log.id),
            "action": log.action.value,
            "ip_address": log.ip_address,
            "details": json.loads(log.details) if log.details else None,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]

    return response_success(
        status=HTTPStatus.OK,
        data=data,
        message="Logs de auditoría obtenidos exitosamente.",
    )

