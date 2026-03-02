class DomainException(Exception):
    """Base para excepciones de dominio"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# ── 404 ──────────────────────────────────────────
class ResourceNotFoundException(DomainException):
    """Recurso no encontrado"""
    pass


# ── 409 ──────────────────────────────────────────
class ResourceAlreadyExistsException(DomainException):
    """Recurso duplicado"""
    pass


# ── 400 ──────────────────────────────────────────
class InvalidOperationException(DomainException):
    """Operación de negocio inválida"""
    pass


# ── 401 ──────────────────────────────────────────
class UnauthorizedException(DomainException):
    """No autenticado o credenciales inválidas"""
    pass


# ── 403 ──────────────────────────────────────────
class ForbiddenException(DomainException):
    """Sin permisos para realizar la operación"""
    pass
