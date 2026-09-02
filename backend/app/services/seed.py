from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User


def seed_admin_user(db: Session):
    if not settings.SEED_ADMIN_EMAIL or not settings.SEED_ADMIN_PASSWORD:
        return
    existing = db.query(User).filter(User.email == settings.SEED_ADMIN_EMAIL).first()
    if existing:
        return
    user = User(
        email=settings.SEED_ADMIN_EMAIL,
        full_name='Free SD Administrator',
        password_hash=hash_password(settings.SEED_ADMIN_PASSWORD),
        role='admin',
        is_active=True,
    )
    db.add(user)
    db.commit()
