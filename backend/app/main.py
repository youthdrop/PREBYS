from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import User
from app.models import youth as youth_models
app = FastAPI(title=settings.app_name)

origins = [
    "https://freesd.org",
    "https://www.freesd.org",
    "https://freesd-2.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_admin() -> None:
    db = SessionLocal()
    try:
        # create admin if missing
        existing = db.query(User).filter(User.role == "admin").first()

        if not existing:
            admin = User(
                email=settings.admin_email,
                full_name="Youth MIS Administrator",
                password_hash=hash_password(settings.admin_password),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print(f"✅ Seeded admin user: {settings.admin_email}")
            return

        # update existing admin email/password if needed
        changed = False

        if existing.email != settings.admin_email:
            existing.email = settings.admin_email
            changed = True

        if not existing.full_name or existing.full_name == "Free SD Administrator":
            existing.full_name = "Youth MIS Administrator"
            changed = True

        # Keep the admin password in sync with Railway ADMIN_PASSWORD/settings.admin_password
        existing.password_hash = hash_password(settings.admin_password)
        changed = True

        if changed:
            db.commit()
            print(f"✅ Admin account updated: {settings.admin_email}")
        else:
            print(f"ℹ️ Admin already exists: {settings.admin_email}")

    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_admin()


@app.get("/")
def root():
    return {"message": "Youth Drop-In Center MIS backend is running"}


app.include_router(api_router)