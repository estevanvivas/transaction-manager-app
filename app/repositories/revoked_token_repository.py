from uuid import UUID

from app.extensions import db
from app.models.revoked_token import RevokedToken, TokenType


class RevokedTokenRepository:

    def add(self, jti: UUID, token_type: TokenType) -> RevokedToken:
        revoked = RevokedToken(jti=jti, token_type=token_type)
        db.session.add(revoked)
        db.session.commit()
        return revoked

    def is_revoked(self, jti: UUID) -> bool:
        return db.session.query(
            db.session.query(RevokedToken)
            .filter_by(jti=jti)
            .exists()
        ).scalar()

