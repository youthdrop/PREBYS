from pathlib import Path
root = Path('/mnt/data/free-sd-suite')
files = {}

def add(path, content):
    files[path] = content.lstrip('\n')

add('README.md', '''
# Free SD Management Information System

This package contains three production-style starter applications for the Free SD program:

- `backend/` — FastAPI + SQLAlchemy + JWT auth + OTP/password reset scaffolding
- `frontend/` — Vite + React + TypeScript web dashboard
- `mobile/` — Expo React Native intake and volunteer app for iOS/Android

## What is included

- Cream / black / white visual theme
- Login with password + two-step verification flow
- Forgot password request + reset flow
- Dashboard with all requested modules
- CRUD endpoints and forms for:
  - Intakes / cases
  - Attorneys
  - Judges
  - Prosecutors / DAs
  - Volunteers
- Reports endpoints and reporting UI
- Role-based delete restriction for admin-only case deletion
- Mobile splash + home + family intake + volunteer signup
- Shared backend APIs for web and mobile

## What still requires your real credentials

For production, you will need to connect:

- PostgreSQL database
- Email provider (SendGrid, Mailgun, SES, etc.)
- SMS provider (Twilio, Vonage, etc.)
- Secure secret keys
- Apple/Google build credentials for the mobile app

The current code includes a development-friendly fallback that logs OTPs and reset links to the backend console if no provider is configured.

## Quick start

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 2) Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 3) Mobile

```bash
cd mobile
npm install
cp .env.example .env
npx expo start
```

## Default dev URLs

- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Expo dev server: provided by Expo CLI

## Recommended production stack

- Backend: Railway / Render / Fly.io / AWS
- Frontend: Vercel / Netlify
- Mobile: Expo EAS Build
- Database: PostgreSQL

## Notes

- The backend seeds an admin user on startup if `SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD` are present.
- The mobile app is intentionally streamlined to the intake and volunteer flows you requested.
- The frontend includes persistent top navigation and logout controls throughout the authenticated area.
''')

add('.gitignore', '''
node_modules/
.venv/
__pycache__/
.env
.env.*
.DS_Store
*.pyc
*.sqlite3
coverage/
dist/
.expo/
.vscode/
.idea/
''')

# backend
add('backend/requirements.txt', '''
fastapi==0.116.1
uvicorn[standard]==0.35.0
sqlalchemy==2.0.43
pydantic==2.11.7
pydantic-settings==2.10.1
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.3
python-multipart==0.0.20
email-validator==2.2.0
alembic==1.16.4
''')

add('backend/.env.example', '''
APP_NAME=Free SD API
API_V1_STR=/api/v1
SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=sqlite:///./free_sd.db
CORS_ORIGINS=http://localhost:5173,http://localhost:19006,http://localhost:8081
OTP_EXPIRE_MINUTES=10
RESET_TOKEN_EXPIRE_MINUTES=60
MAIL_FROM=noreply@freesd.org
EMAIL_PROVIDER=console
SMS_PROVIDER=console
TWILIO_FROM_NUMBER=
FRONTEND_URL=http://localhost:5173
SEED_ADMIN_EMAIL=admin@freesd.org
SEED_ADMIN_PASSWORD=ChangeThis123!
''')

add('backend/app/main.py', '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.services.seed import seed_admin_user

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_admin_user(db)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get('/')
def root():
    return {'message': 'Free SD API running'}
''')

add('backend/app/core/config.py', '''
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = 'Free SD API'
    API_V1_STR: str = '/api/v1'
    SECRET_KEY: str = 'change-me'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = 'sqlite:///./free_sd.db'
    CORS_ORIGINS: str = 'http://localhost:5173'
    OTP_EXPIRE_MINUTES: int = 10
    RESET_TOKEN_EXPIRE_MINUTES: int = 60
    MAIL_FROM: str = 'noreply@freesd.org'
    EMAIL_PROVIDER: str = 'console'
    SMS_PROVIDER: str = 'console'
    TWILIO_FROM_NUMBER: str = ''
    FRONTEND_URL: str = 'http://localhost:5173'
    SEED_ADMIN_EMAIL: str = ''
    SEED_ADMIN_PASSWORD: str = ''

    @property
    def cors_origins_list(self) -> list[str]:
        return [item.strip() for item in self.CORS_ORIGINS.split(',') if item.strip()]

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
''')

add('backend/app/core/security.py', '''
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
ALGORITHM = 'HS256'


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {'sub': subject, 'exp': expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
''')

add('backend/app/db/session.py', '''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

connect_args = {'check_same_thread': False} if settings.DATABASE_URL.startswith('sqlite') else {}
engine = create_engine(settings.DATABASE_URL, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
''')

add('backend/app/db/base.py', '''
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
''')

add('backend/app/db/deps.py', '''
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if not payload or 'sub' not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    user = db.query(User).filter(User.email == payload['sub']).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Administrator access required')
    return current_user
''')

add('backend/app/models/user.py', '''
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default='staff', nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    pending_otp: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pending_otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reset_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
''')

add('backend/app/models/entities.py', '''
from datetime import date, datetime, time
from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Attorney(Base):
    __tablename__ = 'attorneys'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    business_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    note_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cases = relationship('Intake', back_populates='attorney')


class Judge(Base):
    __tablename__ = 'judges'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    clerk_telephone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    courtroom: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    note_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cases = relationship('Intake', back_populates='judge')


class Prosecutor(Base):
    __tablename__ = 'prosecutors'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    note_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cases = relationship('Intake', back_populates='prosecutor')


class Volunteer(Base):
    __tablename__ = 'volunteers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    availability: Mapped[str | None] = mapped_column(Text, nullable=True)
    travel_courts: Mapped[str | None] = mapped_column(Text, nullable=True)
    training_completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    training_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Intake(Base):
    __tablename__ = 'intakes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    case_numbers: Mapped[str | None] = mapped_column(String(255), nullable=True)
    charges: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_person_telephone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_person_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    volunteer_assigned: Mapped[str | None] = mapped_column(String(255), nullable=True)
    maximum_exposure: Mapped[str | None] = mapped_column(String(255), nullable=True)
    court_location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    next_court_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_court_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    court_site: Mapped[str | None] = mapped_column(String(100), nullable=True)
    service_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    case_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    case_note_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    time_saved_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    attorney_id: Mapped[int | None] = mapped_column(ForeignKey('attorneys.id'), nullable=True)
    judge_id: Mapped[int | None] = mapped_column(ForeignKey('judges.id'), nullable=True)
    prosecutor_id: Mapped[int | None] = mapped_column(ForeignKey('prosecutors.id'), nullable=True)

    attorney = relationship('Attorney', back_populates='cases')
    judge = relationship('Judge', back_populates='cases')
    prosecutor = relationship('Prosecutor', back_populates='cases')
''')

add('backend/app/models/__init__.py', 'from app.models.user import User\nfrom app.models.entities import Intake, Attorney, Judge, Prosecutor, Volunteer\n')

add('backend/app/schemas/auth.py', '''
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    delivery_method: str = 'email'


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    code: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    delivery_method: str = 'email'


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: dict
''')

add('backend/app/schemas/common.py', '''
from datetime import date, time, datetime
from pydantic import BaseModel, EmailStr


class AttorneyBase(BaseModel):
    name: str
    business_name: str | None = None
    email: EmailStr | None = None
    telephone: str | None = None
    notes: str | None = None
    note_date: date | None = None


class AttorneyCreate(AttorneyBase):
    pass


class AttorneyRead(AttorneyBase):
    id: int
    case_count: int = 0
    class Config:
        from_attributes = True


class JudgeBase(BaseModel):
    name: str
    clerk_telephone: str | None = None
    courtroom: str | None = None
    notes: str | None = None
    note_date: date | None = None


class JudgeCreate(JudgeBase):
    pass


class JudgeRead(JudgeBase):
    id: int
    case_count: int = 0
    class Config:
        from_attributes = True


class ProsecutorBase(BaseModel):
    name: str
    email: EmailStr | None = None
    telephone: str | None = None
    notes: str | None = None
    note_date: date | None = None


class ProsecutorCreate(ProsecutorBase):
    pass


class ProsecutorRead(ProsecutorBase):
    id: int
    case_count: int = 0
    class Config:
        from_attributes = True


class VolunteerBase(BaseModel):
    name: str
    email: EmailStr | None = None
    telephone: str | None = None
    availability: str | None = None
    travel_courts: str | None = None
    training_completed_date: date | None = None
    training_type: str | None = None
    notes: str | None = None


class VolunteerCreate(VolunteerBase):
    pass


class VolunteerRead(VolunteerBase):
    id: int
    class Config:
        from_attributes = True


class IntakeBase(BaseModel):
    name: str
    case_numbers: str | None = None
    charges: str | None = None
    contact_person: str | None = None
    contact_person_telephone: str | None = None
    contact_person_email: EmailStr | None = None
    volunteer_assigned: str | None = None
    maximum_exposure: str | None = None
    court_location: str | None = None
    next_court_date: date | None = None
    next_court_time: time | None = None
    court_site: str | None = None
    attorney_id: int | None = None
    judge_id: int | None = None
    prosecutor_id: int | None = None
    service_type: str | None = None
    case_note: str | None = None
    case_note_date: date | None = None
    time_saved_hours: float | None = None


class IntakeCreate(IntakeBase):
    attorney: AttorneyCreate | None = None
    judge: JudgeCreate | None = None
    prosecutor: ProsecutorCreate | None = None


class IntakeRead(IntakeBase):
    id: int
    created_at: datetime
    attorney_name: str | None = None
    judge_name: str | None = None
    prosecutor_name: str | None = None
    class Config:
        from_attributes = True
''')

add('backend/app/services/notifications.py', '''
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User


def generate_numeric_code(length: int = 6) -> str:
    value = ''.join(secrets.choice('0123456789') for _ in range(length))
    return value


def send_code(destination: str, code: str, delivery_method: str):
    print(f'[Free SD {delivery_method.upper()}] Sending code to {destination}: {code}')


def send_reset_message(destination: str, token: str, delivery_method: str):
    reset_url = f'{settings.FRONTEND_URL}/reset-password?token={token}'
    print(f'[Free SD {delivery_method.upper()}] Reset link to {destination}: {reset_url}')


def create_and_send_otp(db: Session, user: User, delivery_method: str):
    code = generate_numeric_code()
    user.pending_otp = code
    user.pending_otp_expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    db.add(user)
    db.commit()
    destination = user.email if delivery_method == 'email' else (user.phone or user.email)
    send_code(destination, code, delivery_method)


def create_and_send_reset(db: Session, user: User, delivery_method: str):
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires_at = datetime.utcnow() + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    db.add(user)
    db.commit()
    destination = user.email if delivery_method == 'email' else (user.phone or user.email)
    send_reset_message(destination, token, delivery_method)
''')

add('backend/app/services/seed.py', '''
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
''')

add('backend/app/api/router.py', '''
from fastapi import APIRouter
from app.api import auth, resources, reports

api_router = APIRouter()
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(resources.router, prefix='/resources', tags=['resources'])
api_router.include_router(reports.router, prefix='/reports', tags=['reports'])
''')

add('backend/app/api/auth.py', '''
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.deps import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyOtpRequest,
)
from app.services.notifications import create_and_send_otp, create_and_send_reset

router = APIRouter()


def user_payload(user: User):
    return {'email': user.email, 'full_name': user.full_name, 'role': user.role}


@router.post('/login')
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail='Invalid email or password')
    create_and_send_otp(db, user, payload.delivery_method)
    return {'message': 'Verification code sent'}


@router.post('/verify-otp', response_model=TokenResponse)
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.pending_otp or payload.code != user.pending_otp:
        raise HTTPException(status_code=400, detail='Invalid verification code')
    if not user.pending_otp_expires_at or user.pending_otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail='Verification code expired')
    user.pending_otp = None
    user.pending_otp_expires_at = None
    db.add(user)
    db.commit()
    token = create_access_token(user.email)
    return {'access_token': token, 'user': user_payload(user)}


@router.post('/forgot-password')
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        create_and_send_reset(db, user, payload.delivery_method)
    return {'message': 'If the account exists, a reset message has been sent'}


@router.post('/reset-password')
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == payload.token).first()
    if not user or not user.reset_token_expires_at or user.reset_token_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail='Invalid or expired token')
    user.password_hash = hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expires_at = None
    db.add(user)
    db.commit()
    return {'message': 'Password updated successfully'}
''')

add('backend/app/api/resources.py', '''
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.deps import get_current_user, get_db, require_admin
from app.models.entities import Attorney, Intake, Judge, Prosecutor, Volunteer
from app.schemas.common import (
    AttorneyCreate, AttorneyRead, IntakeCreate, IntakeRead,
    JudgeCreate, JudgeRead, ProsecutorCreate, ProsecutorRead,
    VolunteerCreate, VolunteerRead,
)

router = APIRouter()

COURTS = ['Central', 'Southbay', 'El Cajon', 'Vista', 'Juvenile Court']


def serialize_intake(item: Intake) -> IntakeRead:
    return IntakeRead(
        id=item.id,
        name=item.name,
        case_numbers=item.case_numbers,
        charges=item.charges,
        contact_person=item.contact_person,
        contact_person_telephone=item.contact_person_telephone,
        contact_person_email=item.contact_person_email,
        volunteer_assigned=item.volunteer_assigned,
        maximum_exposure=item.maximum_exposure,
        court_location=item.court_location,
        next_court_date=item.next_court_date,
        next_court_time=item.next_court_time,
        court_site=item.court_site,
        attorney_id=item.attorney_id,
        judge_id=item.judge_id,
        prosecutor_id=item.prosecutor_id,
        service_type=item.service_type,
        case_note=item.case_note,
        case_note_date=item.case_note_date,
        time_saved_hours=item.time_saved_hours,
        created_at=item.created_at,
        attorney_name=item.attorney.name if item.attorney else None,
        judge_name=item.judge.name if item.judge else None,
        prosecutor_name=item.prosecutor.name if item.prosecutor else None,
    )


def upsert_related(db: Session, payload: IntakeCreate):
    attorney_id = payload.attorney_id
    judge_id = payload.judge_id
    prosecutor_id = payload.prosecutor_id
    if payload.attorney:
        obj = Attorney(**payload.attorney.model_dump())
        db.add(obj)
        db.flush()
        attorney_id = obj.id
    if payload.judge:
        obj = Judge(**payload.judge.model_dump())
        db.add(obj)
        db.flush()
        judge_id = obj.id
    if payload.prosecutor:
        obj = Prosecutor(**payload.prosecutor.model_dump())
        db.add(obj)
        db.flush()
        prosecutor_id = obj.id
    return attorney_id, judge_id, prosecutor_id


@router.get('/lookups')
def lookups(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        'courts': COURTS,
        'attorneys': [AttorneyRead.model_validate({**a.__dict__, 'case_count': len(a.cases)}) for a in db.query(Attorney).order_by(Attorney.name).all()],
        'judges': [JudgeRead.model_validate({**j.__dict__, 'case_count': len(j.cases)}) for j in db.query(Judge).order_by(Judge.name).all()],
        'prosecutors': [ProsecutorRead.model_validate({**p.__dict__, 'case_count': len(p.cases)}) for p in db.query(Prosecutor).order_by(Prosecutor.name).all()],
        'volunteers': [VolunteerRead.model_validate(v) for v in db.query(Volunteer).order_by(Volunteer.name).all()],
    }


@router.post('/intakes', response_model=IntakeRead)
def create_intake(payload: IntakeCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    attorney_id, judge_id, prosecutor_id = upsert_related(db, payload)
    obj = Intake(**payload.model_dump(exclude={'attorney', 'judge', 'prosecutor'}), attorney_id=attorney_id, judge_id=judge_id, prosecutor_id=prosecutor_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return serialize_intake(obj)


@router.get('/intakes', response_model=list[IntakeRead])
def list_intakes(search: str = Query(default=''), current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Intake)
    if search:
        like = f'%{search}%'
        q = q.filter(or_(Intake.name.ilike(like), Intake.case_numbers.ilike(like), Intake.contact_person.ilike(like)))
    items = q.order_by(Intake.next_court_date.asc().nullslast(), Intake.name.asc()).all()
    return [serialize_intake(item) for item in items]


@router.get('/intakes/{intake_id}', response_model=IntakeRead)
def get_intake(intake_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    obj = db.get(Intake, intake_id)
    if not obj:
        raise HTTPException(404, 'Case not found')
    return serialize_intake(obj)


@router.put('/intakes/{intake_id}', response_model=IntakeRead)
def update_intake(intake_id: int, payload: IntakeCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    obj = db.get(Intake, intake_id)
    if not obj:
        raise HTTPException(404, 'Case not found')
    attorney_id, judge_id, prosecutor_id = upsert_related(db, payload)
    for key, value in payload.model_dump(exclude={'attorney', 'judge', 'prosecutor'}).items():
        setattr(obj, key, value)
    obj.attorney_id = attorney_id
    obj.judge_id = judge_id
    obj.prosecutor_id = prosecutor_id
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return serialize_intake(obj)


@router.delete('/intakes/{intake_id}')
def delete_intake(intake_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    obj = db.get(Intake, intake_id)
    if not obj:
        raise HTTPException(404, 'Case not found')
    db.delete(obj)
    db.commit()
    return {'message': 'Case deleted'}


def crud_routes(path: str, model, create_schema, read_schema):
    @router.post(path, response_model=read_schema)
    def create_item(payload: create_schema, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
        obj = model(**payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        data = obj.__dict__.copy()
        if hasattr(obj, 'cases'):
            data['case_count'] = len(obj.cases)
        return read_schema.model_validate(data)

    @router.get(path, response_model=list[read_schema])
    def list_items(search: str = Query(default=''), current_user=Depends(get_current_user), db: Session = Depends(get_db)):
        q = db.query(model)
        if search and hasattr(model, 'name'):
            q = q.filter(model.name.ilike(f'%{search}%'))
        items = q.order_by(model.name.asc()).all()
        results = []
        for item in items:
            data = item.__dict__.copy()
            if hasattr(item, 'cases'):
                data['case_count'] = len(item.cases)
            results.append(read_schema.model_validate(data))
        return results

    @router.get(f'{path}/{{item_id}}', response_model=read_schema)
    def get_item(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
        item = db.get(model, item_id)
        if not item:
            raise HTTPException(404, 'Not found')
        data = item.__dict__.copy()
        if hasattr(item, 'cases'):
            data['case_count'] = len(item.cases)
        return read_schema.model_validate(data)

    @router.put(f'{path}/{{item_id}}', response_model=read_schema)
    def update_item(item_id: int, payload: create_schema, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
        item = db.get(model, item_id)
        if not item:
            raise HTTPException(404, 'Not found')
        for key, value in payload.model_dump().items():
            setattr(item, key, value)
        db.add(item)
        db.commit()
        db.refresh(item)
        data = item.__dict__.copy()
        if hasattr(item, 'cases'):
            data['case_count'] = len(item.cases)
        return read_schema.model_validate(data)

    @router.delete(f'{path}/{{item_id}}')
    def delete_item(item_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
        item = db.get(model, item_id)
        if not item:
            raise HTTPException(404, 'Not found')
        db.delete(item)
        db.commit()
        return {'message': 'Deleted'}

crud_routes('/attorneys', Attorney, AttorneyCreate, AttorneyRead)
crud_routes('/judges', Judge, JudgeCreate, JudgeRead)
crud_routes('/prosecutors', Prosecutor, ProsecutorCreate, ProsecutorRead)
crud_routes('/volunteers', Volunteer, VolunteerCreate, VolunteerRead)


@router.post('/public/family-intake')
def public_family_intake(payload: IntakeCreate, db: Session = Depends(get_db)):
    obj = Intake(**payload.model_dump(exclude={'attorney', 'judge', 'prosecutor'}))
    db.add(obj)
    db.commit()
    return {'message': 'Intake submitted successfully'}


@router.post('/public/volunteer-signup')
def public_volunteer_signup(payload: VolunteerCreate, db: Session = Depends(get_db)):
    obj = Volunteer(**payload.model_dump())
    db.add(obj)
    db.commit()
    return {'message': 'Volunteer signup submitted successfully'}
''')

add('backend/app/api/reports.py', '''
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.deps import get_current_user, get_db
from app.models.entities import Intake

router = APIRouter()


@router.get('/summary')
def reports_summary(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Intake)
    if start_date:
        q = q.filter(Intake.created_at >= start_date)
    if end_date:
        q = q.filter(Intake.created_at <= end_date)
    items = q.all()
    return {
        'intakes_count': len(items),
        'time_saved_total': round(sum(item.time_saved_hours or 0 for item in items), 2),
        'by_judge': sorted([
            {'judge': k, 'count': v} for k, v in _group_counts(items, 'judge')
        ], key=lambda x: x['count'], reverse=True),
        'by_prosecutor': sorted([
            {'prosecutor': k, 'count': v} for k, v in _group_counts(items, 'prosecutor')
        ], key=lambda x: x['count'], reverse=True),
        'court_dates': [
            {
                'name': item.name,
                'case_numbers': item.case_numbers,
                'next_court_date': item.next_court_date,
                'next_court_time': item.next_court_time,
                'court_site': item.court_site,
            }
            for item in items if item.next_court_date
        ],
    }


def _group_counts(items, relation_name: str):
    counts = {}
    for item in items:
        rel = getattr(item, relation_name)
        name = rel.name if rel else 'Unassigned'
        counts[name] = counts.get(name, 0) + 1
    return counts.items()
''')

# frontend package
add('frontend/package.json', '''
{
  "name": "free-sd-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.11.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.30.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.23",
    "@types/react-dom": "^18.3.7",
    "@vitejs/plugin-react": "^4.7.0",
    "typescript": "^5.9.2",
    "vite": "^5.4.19"
  }
}
''')

add('frontend/tsconfig.json', '''
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "Node",
    "allowSyntheticDefaultImports": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": false
  },
  "include": ["src"]
}
''')

add('frontend/vite.config.ts', '''
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { port: 5173 }
})
''')

add('frontend/.env.example', 'VITE_API_URL=http://localhost:8000/api/v1\n')
add('frontend/index.html', '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Free SD</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''')

add('frontend/src/main.tsx', '''
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './contexts/AuthContext'
import './styles/global.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
)
''')

add('frontend/src/App.tsx', '''
import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import LoginPage from './pages/LoginPage'
import VerifyOtpPage from './pages/VerifyOtpPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import DashboardPage from './pages/DashboardPage'
import EntityListPage from './pages/EntityListPage'
import EntityFormPage from './pages/EntityFormPage'
import IntakeListPage from './pages/IntakeListPage'
import IntakeFormPage from './pages/IntakeFormPage'
import IntakeDetailsPage from './pages/IntakeDetailsPage'
import ReportsPage from './pages/ReportsPage'

function Protected({ children }: { children: JSX.Element }) {
  const { token } = useAuth()
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/verify-otp" element={<VerifyOtpPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/" element={<Protected><DashboardPage /></Protected>} />
      <Route path="/intakes" element={<Protected><IntakeListPage /></Protected>} />
      <Route path="/intakes/new" element={<Protected><IntakeFormPage /></Protected>} />
      <Route path="/intakes/:id" element={<Protected><IntakeDetailsPage /></Protected>} />
      <Route path="/attorneys" element={<Protected><EntityListPage entity="attorneys" /></Protected>} />
      <Route path="/attorneys/new" element={<Protected><EntityFormPage entity="attorneys" /></Protected>} />
      <Route path="/judges" element={<Protected><EntityListPage entity="judges" /></Protected>} />
      <Route path="/judges/new" element={<Protected><EntityFormPage entity="judges" /></Protected>} />
      <Route path="/prosecutors" element={<Protected><EntityListPage entity="prosecutors" /></Protected>} />
      <Route path="/prosecutors/new" element={<Protected><EntityFormPage entity="prosecutors" /></Protected>} />
      <Route path="/volunteers" element={<Protected><EntityListPage entity="volunteers" /></Protected>} />
      <Route path="/volunteers/new" element={<Protected><EntityFormPage entity="volunteers" /></Protected>} />
      <Route path="/reports" element={<Protected><ReportsPage /></Protected>} />
    </Routes>
  )
}
''')

add('frontend/src/api/client.ts', '''
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('free_sd_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default api
''')

add('frontend/src/contexts/AuthContext.tsx', '''
import { createContext, useEffect, useMemo, useState } from 'react'

type User = { email: string; full_name?: string; role: string } | null

type AuthContextType = {
  token: string | null
  user: User
  setSession: (token: string, user: NonNullable<User>) => void
  logout: () => void
}

export const AuthContext = createContext<AuthContextType>({
  token: null,
  user: null,
  setSession: () => {},
  logout: () => {}
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('free_sd_token'))
  const [user, setUser] = useState<User>(JSON.parse(localStorage.getItem('free_sd_user') || 'null'))

  const setSession = (newToken: string, newUser: NonNullable<User>) => {
    localStorage.setItem('free_sd_token', newToken)
    localStorage.setItem('free_sd_user', JSON.stringify(newUser))
    setToken(newToken)
    setUser(newUser)
  }

  const logout = () => {
    localStorage.removeItem('free_sd_token')
    localStorage.removeItem('free_sd_user')
    setToken(null)
    setUser(null)
  }

  const value = useMemo(() => ({ token, user, setSession, logout }), [token, user])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
''')

add('frontend/src/hooks/useAuth.ts', '''
import { useContext } from 'react'
import { AuthContext } from '../contexts/AuthContext'

export const useAuth = () => useContext(AuthContext)
''')

add('frontend/src/components/TopNav.tsx', '''
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function TopNav() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  return (
    <header className="topnav">
      <div className="brand">Free SD</div>
      <nav>
        <Link to="/">Dashboard</Link>
        <Link to="/intakes">Intakes</Link>
        <Link to="/attorneys">Attorneys</Link>
        <Link to="/judges">Judges</Link>
        <Link to="/prosecutors">DAs</Link>
        <Link to="/volunteers">Volunteers</Link>
        <Link to="/reports">Reports</Link>
      </nav>
      <div className="nav-actions">
        <span>{user?.role}</span>
        <button onClick={() => { logout(); navigate('/login') }}>Log out</button>
      </div>
    </header>
  )
}
''')

add('frontend/src/layouts/AppShell.tsx', '''
import TopNav from '../components/TopNav'

export default function AppShell({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <TopNav />
      <main className="content-wrap">
        <div className="page-header">
          <h1>{title}</h1>
        </div>
        {children}
      </main>
    </div>
  )
}
''')

add('frontend/src/pages/LoginPage.tsx', '''
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/client'

export default function LoginPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '', delivery_method: 'email' })
  const [message, setMessage] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    const { data } = await api.post('/auth/login', form)
    setMessage(data.message)
    sessionStorage.setItem('otp_email', form.email)
    navigate('/verify-otp')
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <div className="logo-circle">FS</div>
        <h1>Free SD</h1>
        <p>Secure login with two-step verification.</p>
        <input placeholder="Email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
        <input type="password" placeholder="Password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
        <select value={form.delivery_method} onChange={e => setForm({ ...form, delivery_method: e.target.value })}>
          <option value="email">Email code</option>
          <option value="text">Text code</option>
        </select>
        <button type="submit">Send verification code</button>
        {message && <div className="status">{message}</div>}
        <Link to="/forgot-password">Forgot password?</Link>
      </form>
    </div>
  )
}
''')

add('frontend/src/pages/VerifyOtpPage.tsx', '''
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../hooks/useAuth'

export default function VerifyOtpPage() {
  const navigate = useNavigate()
  const { setSession } = useAuth()
  const email = sessionStorage.getItem('otp_email') || ''
  const [code, setCode] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    const { data } = await api.post('/auth/verify-otp', { email, code })
    setSession(data.access_token, data.user)
    navigate('/')
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <h1>Enter verification code</h1>
        <p>{email}</p>
        <input placeholder="6-digit code" value={code} onChange={e => setCode(e.target.value)} />
        <button type="submit">Verify and continue</button>
      </form>
    </div>
  )
}
''')

add('frontend/src/pages/ForgotPasswordPage.tsx', '''
import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [delivery_method, setMethod] = useState('email')
  const [message, setMessage] = useState('')
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    const { data } = await api.post('/auth/forgot-password', { email, delivery_method })
    setMessage(data.message)
  }
  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <h1>Forgot password</h1>
        <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <select value={delivery_method} onChange={e => setMethod(e.target.value)}>
          <option value="email">Email link</option>
          <option value="text">Text link</option>
        </select>
        <button type="submit">Send reset link</button>
        {message && <div className="status">{message}</div>}
        <Link to="/login">Back to login</Link>
      </form>
    </div>
  )
}
''')

add('frontend/src/pages/ResetPasswordPage.tsx', '''
import { useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import api from '../api/client'

export default function ResetPasswordPage() {
  const location = useLocation()
  const token = useMemo(() => new URLSearchParams(location.search).get('token') || '', [location.search])
  const [newPassword, setNewPassword] = useState('')
  const [message, setMessage] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    const { data } = await api.post('/auth/reset-password', { token, new_password: newPassword })
    setMessage(data.message)
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <h1>Reset password</h1>
        <input type="password" placeholder="New password" value={newPassword} onChange={e => setNewPassword(e.target.value)} />
        <button type="submit">Save new password</button>
        {message && <div className="status">{message}</div>}
        <Link to="/login">Back to login</Link>
      </form>
    </div>
  )
}
''')

add('frontend/src/pages/DashboardPage.tsx', '''
import { Link } from 'react-router-dom'
import AppShell from '../layouts/AppShell'

const cards = [
  ['Add Intake', '/intakes/new'],
  ['View Intake Database', '/intakes'],
  ['Add Attorney', '/attorneys/new'],
  ['View Attorney Database', '/attorneys'],
  ['Add Judge', '/judges/new'],
  ['View Judge Database', '/judges'],
  ['Add DA', '/prosecutors/new'],
  ['View DA Database', '/prosecutors'],
  ['Add Volunteer', '/volunteers/new'],
  ['View Volunteer Database', '/volunteers'],
  ['Run Reports', '/reports'],
]

export default function DashboardPage() {
  return (
    <AppShell title="Dashboard">
      <div className="grid">
        {cards.map(([label, path]) => (
          <Link key={label} to={path} className="tile">{label}</Link>
        ))}
      </div>
    </AppShell>
  )
}
''')

add('frontend/src/pages/IntakeListPage.tsx', '''
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'
import { useAuth } from '../hooks/useAuth'

export default function IntakeListPage() {
  const { user } = useAuth()
  const [items, setItems] = useState<any[]>([])
  const [search, setSearch] = useState('')

  const load = async () => {
    const { data } = await api.get('/resources/intakes', { params: { search } })
    setItems(data)
  }

  useEffect(() => { load() }, [search])

  const remove = async (id: number) => {
    await api.delete(`/resources/intakes/${id}`)
    load()
  }

  return (
    <AppShell title="Intake Database">
      <div className="toolbar">
        <input placeholder="Search cases" value={search} onChange={e => setSearch(e.target.value)} />
        <Link className="button-link" to="/intakes/new">Add Intake</Link>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th><th>Case #</th><th>Next court date</th><th>Time</th><th>Location</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => (
            <tr key={item.id}>
              <td>{item.name}</td>
              <td>{item.case_numbers}</td>
              <td>{item.next_court_date || ''}</td>
              <td>{item.next_court_time || ''}</td>
              <td>{item.court_site || item.court_location || ''}</td>
              <td>
                <Link to={`/intakes/${item.id}`}>Details</Link>
                {user?.role === 'admin' && <button onClick={() => remove(item.id)}>Delete</button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </AppShell>
  )
}
''')

add('frontend/src/pages/IntakeFormPage.tsx', '''
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

const empty = {
  name: '', case_numbers: '', charges: '', contact_person: '', contact_person_telephone: '',
  contact_person_email: '', volunteer_assigned: '', maximum_exposure: '', court_location: '',
  next_court_date: '', next_court_time: '', court_site: 'Central', attorney_id: '', judge_id: '',
  prosecutor_id: '', service_type: 'Social bio', case_note: '', case_note_date: '', time_saved_hours: ''
}

export default function IntakeFormPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<any>(empty)
  const [lookups, setLookups] = useState<any>({ courts: [], attorneys: [], judges: [], prosecutors: [] })
  useEffect(() => { api.get('/resources/lookups').then(({ data }) => setLookups(data)) }, [])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.post('/resources/intakes', {
      ...form,
      attorney_id: form.attorney_id ? Number(form.attorney_id) : null,
      judge_id: form.judge_id ? Number(form.judge_id) : null,
      prosecutor_id: form.prosecutor_id ? Number(form.prosecutor_id) : null,
      time_saved_hours: form.time_saved_hours ? Number(form.time_saved_hours) : null
    })
    navigate('/intakes')
  }

  return (
    <AppShell title="Add Intake">
      <form className="form-grid" onSubmit={submit}>
        {Object.entries(empty).map(([key]) => (
          key === 'attorney_id' ? (
            <label key={key}>Attorney
              <select value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })}>
                <option value="">Select attorney</option>
                {lookups.attorneys.map((item: any) => <option key={item.id} value={item.id}>{item.name}</option>)}
              </select>
            </label>
          ) : key === 'judge_id' ? (
            <label key={key}>Judge
              <select value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })}>
                <option value="">Select judge</option>
                {lookups.judges.map((item: any) => <option key={item.id} value={item.id}>{item.name}</option>)}
              </select>
            </label>
          ) : key === 'prosecutor_id' ? (
            <label key={key}>DA / Prosecutor
              <select value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })}>
                <option value="">Select prosecutor</option>
                {lookups.prosecutors.map((item: any) => <option key={item.id} value={item.id}>{item.name}</option>)}
              </select>
            </label>
          ) : key === 'court_site' ? (
            <label key={key}>Court
              <select value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })}>
                {lookups.courts.map((item: string) => <option key={item}>{item}</option>)}
              </select>
            </label>
          ) : key === 'service_type' ? (
            <label key={key}>Type of Service
              <select value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })}>
                {['Social bio', 'In person', 'Court', 'Meeting with attorney', 'Phone call'].map(item => <option key={item}>{item}</option>)}
              </select>
            </label>
          ) : (
            <label key={key}>{key.replaceAll('_', ' ')}
              <input type={key.includes('date') ? 'date' : key.includes('time') ? 'time' : 'text'} value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })} />
            </label>
          )
        ))}
        <button type="submit">Save Intake</button>
      </form>
    </AppShell>
  )
}
''')

add('frontend/src/pages/IntakeDetailsPage.tsx', '''
import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

export default function IntakeDetailsPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState<any | null>(null)
  const [lookups, setLookups] = useState<any>({ courts: [], attorneys: [], judges: [], prosecutors: [] })
  useEffect(() => {
    api.get('/resources/lookups').then(({ data }) => setLookups(data))
    api.get(`/resources/intakes/${id}`).then(({ data }) => setForm({ ...data, attorney_id: data.attorney_id || '', judge_id: data.judge_id || '', prosecutor_id: data.prosecutor_id || '' }))
  }, [id])
  if (!form) return <AppShell title="Case Details"><div>Loading...</div></AppShell>
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.put(`/resources/intakes/${id}`, {
      ...form,
      attorney_id: form.attorney_id ? Number(form.attorney_id) : null,
      judge_id: form.judge_id ? Number(form.judge_id) : null,
      prosecutor_id: form.prosecutor_id ? Number(form.prosecutor_id) : null,
    })
    navigate('/intakes')
  }
  return (
    <AppShell title={`Case Details: ${form.name}`}>
      <div className="summary-banner">Case number: {form.case_numbers || 'N/A'}</div>
      <form className="form-grid" onSubmit={submit}>
        {Object.keys(form).filter(k => !['id','created_at','attorney_name','judge_name','prosecutor_name'].includes(k)).map(key => (
          key === 'attorney_id' ? <label key={key}>Attorney<select value={form[key] || ''} onChange={e => setForm({ ...form, [key]: e.target.value })}><option value="">Select</option>{lookups.attorneys.map((i: any) => <option key={i.id} value={i.id}>{i.name}</option>)}</select></label>
          : key === 'judge_id' ? <label key={key}>Judge<select value={form[key] || ''} onChange={e => setForm({ ...form, [key]: e.target.value })}><option value="">Select</option>{lookups.judges.map((i: any) => <option key={i.id} value={i.id}>{i.name}</option>)}</select></label>
          : key === 'prosecutor_id' ? <label key={key}>DA / Prosecutor<select value={form[key] || ''} onChange={e => setForm({ ...form, [key]: e.target.value })}><option value="">Select</option>{lookups.prosecutors.map((i: any) => <option key={i.id} value={i.id}>{i.name}</option>)}</select></label>
          : <label key={key}>{key.replaceAll('_',' ')}<input disabled={key === 'name' || key === 'case_numbers'} type={key.includes('date') ? 'date' : key.includes('time') ? 'time' : 'text'} value={form[key] || ''} onChange={e => setForm({ ...form, [key]: e.target.value })} /></label>
        ))}
        <button type="submit">Save Changes</button>
        <Link className="button-link" to="/intakes">Return to intake database</Link>
      </form>
    </AppShell>
  )
}
''')

add('frontend/src/pages/EntityListPage.tsx', '''
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'
import { useAuth } from '../hooks/useAuth'

const labels: Record<string, string> = { attorneys: 'Attorney Database', judges: 'Judge Database', prosecutors: 'DA / Prosecutor Database', volunteers: 'Volunteer Database' }

export default function EntityListPage({ entity }: { entity: string }) {
  const { user } = useAuth()
  const [items, setItems] = useState<any[]>([])
  const [search, setSearch] = useState('')
  const load = async () => {
    const { data } = await api.get(`/resources/${entity}`, { params: { search } })
    setItems(data)
  }
  useEffect(() => { load() }, [search, entity])
  const remove = async (id: number) => { await api.delete(`/resources/${entity}/${id}`); load() }
  return (
    <AppShell title={labels[entity]}>
      <div className="toolbar">
        <input placeholder={`Search ${entity}`} value={search} onChange={e => setSearch(e.target.value)} />
        <Link className="button-link" to={`/${entity}/new`}>Add New</Link>
      </div>
      <table className="data-table">
        <thead><tr><th>Name</th><th>Email</th><th>Telephone</th><th>Cases</th><th>Actions</th></tr></thead>
        <tbody>
          {items.map(item => (
            <tr key={item.id}>
              <td>{item.name}</td><td>{item.email || ''}</td><td>{item.telephone || item.clerk_telephone || ''}</td><td>{item.case_count || ''}</td>
              <td>{user?.role === 'admin' && <button onClick={() => remove(item.id)}>Delete</button>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </AppShell>
  )
}
''')

add('frontend/src/pages/EntityFormPage.tsx', '''
import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

const fields: Record<string, string[]> = {
  attorneys: ['name', 'business_name', 'email', 'telephone', 'notes', 'note_date'],
  judges: ['name', 'clerk_telephone', 'courtroom', 'notes', 'note_date'],
  prosecutors: ['name', 'email', 'telephone', 'notes', 'note_date'],
  volunteers: ['name', 'email', 'telephone', 'availability', 'travel_courts', 'training_completed_date', 'training_type', 'notes']
}

export default function EntityFormPage({ entity }: { entity: string }) {
  const navigate = useNavigate()
  const initial = useMemo(() => Object.fromEntries(fields[entity].map(key => [key, ''])), [entity])
  const [form, setForm] = useState<any>(initial)
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.post(`/resources/${entity}`, form)
    navigate(`/${entity}`)
  }
  return (
    <AppShell title={`Add ${entity.slice(0, -1)}`}>
      <form className="form-grid" onSubmit={submit}>
        {fields[entity].map(key => (
          <label key={key}>{key.replaceAll('_', ' ')}
            <input type={key.includes('date') ? 'date' : 'text'} value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })} />
          </label>
        ))}
        <button type="submit">Save</button>
      </form>
    </AppShell>
  )
}
''')

add('frontend/src/pages/ReportsPage.tsx', '''
import { useState } from 'react'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

export default function ReportsPage() {
  const [filters, setFilters] = useState({ start_date: '', end_date: '' })
  const [data, setData] = useState<any | null>(null)

  const run = async () => {
    const response = await api.get('/reports/summary', { params: filters })
    setData(response.data)
  }

  return (
    <AppShell title="Reports">
      <div className="toolbar">
        <label>Start date <input type="date" value={filters.start_date} onChange={e => setFilters({ ...filters, start_date: e.target.value })} /></label>
        <label>End date <input type="date" value={filters.end_date} onChange={e => setFilters({ ...filters, end_date: e.target.value })} /></label>
        <button onClick={run}>Run reports</button>
      </div>
      {data && (
        <div className="report-grid">
          <div className="report-card"><h3>Time Saved Report</h3><p>{data.time_saved_total} hours</p></div>
          <div className="report-card"><h3>Intake Report</h3><p>{data.intakes_count} intakes</p></div>
          <div className="report-card"><h3>DA Report</h3><pre>{JSON.stringify(data.by_prosecutor, null, 2)}</pre></div>
          <div className="report-card"><h3>Judge Report</h3><pre>{JSON.stringify(data.by_judge, null, 2)}</pre></div>
          <div className="report-card wide"><h3>Court Dates</h3><pre>{JSON.stringify(data.court_dates, null, 2)}</pre></div>
        </div>
      )}
    </AppShell>
  )
}
''')

add('frontend/src/styles/global.css', '''
:root {
  --cream: #efe5d5;
  --ink: #111111;
  --paper: #ffffff;
  --line: #ddd4c7;
}
* { box-sizing: border-box; }
body { margin: 0; font-family: Arial, Helvetica, sans-serif; color: var(--ink); background: var(--paper); }
a { color: var(--ink); text-decoration: none; }
button, .button-link { background: var(--ink); color: white; border: none; border-radius: 10px; padding: 0.8rem 1rem; cursor: pointer; display: inline-block; }
input, select, textarea { width: 100%; padding: 0.8rem; border: 1px solid var(--line); border-radius: 10px; background: #fff; }
label { display: grid; gap: 0.4rem; font-size: 0.95rem; }
.topnav { position: sticky; top: 0; z-index: 100; background: var(--paper); border-bottom: 1px solid var(--line); display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; gap: 1rem; }
.topnav nav { display: flex; gap: 1rem; flex-wrap: wrap; }
.nav-actions { display: flex; align-items: center; gap: 1rem; }
.brand { font-size: 1.25rem; font-weight: 700; }
.content-wrap { padding: 1.5rem; max-width: 1300px; margin: 0 auto; }
.page-header { margin-bottom: 1rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }
.tile { background: var(--cream); padding: 1.4rem; border-radius: 18px; border: 1px solid var(--line); min-height: 120px; display: flex; align-items: center; font-weight: 700; }
.auth-page { min-height: 100vh; display: grid; place-items: center; background: linear-gradient(180deg, #fff, var(--cream)); }
.auth-card { width: min(420px, 92vw); background: white; border: 1px solid var(--line); border-radius: 22px; padding: 2rem; display: grid; gap: 1rem; box-shadow: 0 12px 32px rgba(0,0,0,0.06); }
.logo-circle { width: 70px; height: 70px; border-radius: 999px; background: var(--ink); color: white; display: grid; place-items: center; font-weight: 700; }
.status, .summary-banner { background: var(--cream); padding: 1rem; border-radius: 12px; }
.toolbar { display: flex; gap: 1rem; flex-wrap: wrap; align-items: end; margin-bottom: 1rem; }
.data-table { width: 100%; border-collapse: collapse; border: 1px solid var(--line); }
.data-table th, .data-table td { padding: 0.8rem; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }
.form-grid button, .form-grid .button-link { align-self: end; }
.report-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-top: 1rem; }
.report-card { background: var(--cream); border-radius: 18px; padding: 1rem; border: 1px solid var(--line); }
.report-card.wide { grid-column: 1 / -1; }
@media (max-width: 900px) { .topnav { flex-direction: column; align-items: flex-start; } }
''')

# mobile
add('mobile/package.json', '''
{
  "name": "free-sd-mobile",
  "version": "0.1.0",
  "private": true,
  "main": "expo-router/entry",
  "scripts": {
    "start": "expo start",
    "android": "expo run:android",
    "ios": "expo run:ios",
    "web": "expo start --web"
  },
  "dependencies": {
    "expo": "~54.0.0",
    "expo-router": "~4.0.17",
    "expo-splash-screen": "~0.31.8",
    "react": "19.0.0",
    "react-native": "0.81.4",
    "react-native-safe-area-context": "4.14.1",
    "react-native-screens": "~4.11.1"
  }
}
''')

add('mobile/app.json', '''
{
  "expo": {
    "name": "Free SD",
    "slug": "free-sd-mobile",
    "scheme": "freesd",
    "plugins": ["expo-router"],
    "splash": {
      "backgroundColor": "#ffffff",
      "resizeMode": "contain"
    },
    "ios": { "supportsTablet": true },
    "android": {},
    "extra": { "router": {} }
  }
}
''')

add('mobile/babel.config.js', '''
module.exports = function(api) {
  api.cache(true)
  return {
    presets: ['babel-preset-expo'],
    plugins: ['expo-router/babel'],
  }
}
''')

add('mobile/.env.example', 'EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1\n')

add('mobile/constants/theme.ts', '''
export const theme = {
  cream: '#efe5d5',
  black: '#111111',
  white: '#ffffff',
  line: '#ddd4c7'
}
''')

add('mobile/services/api.ts', '''
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export async function postJson(path: string, payload: any) {
  const res = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Request failed')
  return data
}
''')

add('mobile/components/AppScaffold.tsx', '''
import { ReactNode } from 'react'
import { SafeAreaView, StyleSheet, Text, TouchableOpacity, View } from 'react-native'
import { router } from 'expo-router'
import { theme } from '../constants/theme'

export default function AppScaffold({ title, children }: { title: string; children: ReactNode }) {
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.navbar}>
        <TouchableOpacity onPress={() => router.replace('/')}><Text style={styles.navText}>Home</Text></TouchableOpacity>
        <Text style={styles.title}>Free SD</Text>
        <TouchableOpacity onPress={() => router.back()}><Text style={styles.navText}>Back</Text></TouchableOpacity>
      </View>
      <View style={styles.container}>
        <Text style={styles.pageTitle}>{title}</Text>
        {children}
      </View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: theme.white },
  navbar: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: theme.line },
  navText: { color: theme.black, fontWeight: '700' },
  title: { fontSize: 18, fontWeight: '700', color: theme.black },
  container: { padding: 20, gap: 16 },
  pageTitle: { fontSize: 28, fontWeight: '700', color: theme.black }
})
''')

add('mobile/app/_layout.tsx', '''
import { Stack } from 'expo-router'

export default function Layout() {
  return <Stack screenOptions={{ headerShown: false }} />
}
''')

add('mobile/app/index.tsx', '''
import { router } from 'expo-router'
import { Image, StyleSheet, Text, TouchableOpacity, View } from 'react-native'
import AppScaffold from '../components/AppScaffold'
import { theme } from '../constants/theme'

export default function HomeScreen() {
  return (
    <AppScaffold title="Welcome">
      <View style={styles.logoWrap}><Text style={styles.logo}>FS</Text></View>
      <TouchableOpacity style={styles.button} onPress={() => router.push('/family-intake')}>
        <Text style={styles.buttonText}>Families</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.button} onPress={() => router.push('/volunteer-signup')}>
        <Text style={styles.buttonText}>Volunteers</Text>
      </TouchableOpacity>
    </AppScaffold>
  )
}

const styles = StyleSheet.create({
  logoWrap: { alignItems: 'center', marginVertical: 24 },
  logo: { width: 96, height: 96, textAlign: 'center', textAlignVertical: 'center', lineHeight: 96, borderRadius: 48, overflow: 'hidden', backgroundColor: theme.black, color: theme.white, fontWeight: '700', fontSize: 28 },
  button: { backgroundColor: theme.black, padding: 18, borderRadius: 14, marginBottom: 14 },
  buttonText: { color: theme.white, fontWeight: '700', fontSize: 18, textAlign: 'center' }
})
''')

add('mobile/app/family-intake.tsx', '''
import { useState } from 'react'
import { Alert, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native'
import AppScaffold from '../components/AppScaffold'
import { theme } from '../constants/theme'
import { postJson } from '../services/api'

export default function FamilyIntakeScreen() {
  const [form, setForm] = useState({
    name: '', case_numbers: '', charges: '', contact_person: '', contact_person_telephone: '', contact_person_email: ''
  })

  const submit = async () => {
    if (!form.name || !form.contact_person || !form.contact_person_telephone || !form.contact_person_email) {
      Alert.alert('Required fields', 'Please complete all required fields.')
      return
    }
    try {
      await postJson('/resources/public/family-intake', form)
      Alert.alert('Submitted', 'Your intake has been submitted.')
      setForm({ name: '', case_numbers: '', charges: '', contact_person: '', contact_person_telephone: '', contact_person_email: '' })
    } catch (error: any) {
      Alert.alert('Error', error.message)
    }
  }

  return (
    <AppScaffold title="Family Intake">
      <ScrollView contentContainerStyle={styles.form}>
        {Object.keys(form).map((key) => (
          <View key={key}>
            <Text style={styles.label}>{key.replaceAll('_', ' ')}</Text>
            <TextInput style={styles.input} value={(form as any)[key]} onChangeText={(text) => setForm({ ...form, [key]: text })} />
          </View>
        ))}
        <TouchableOpacity style={styles.button} onPress={submit}><Text style={styles.buttonText}>Submit</Text></TouchableOpacity>
      </ScrollView>
    </AppScaffold>
  )
}

const styles = StyleSheet.create({
  form: { gap: 12, paddingBottom: 24 },
  label: { fontWeight: '700', color: theme.black, marginBottom: 6 },
  input: { borderWidth: 1, borderColor: theme.line, backgroundColor: theme.white, borderRadius: 12, padding: 14 },
  button: { backgroundColor: theme.black, padding: 16, borderRadius: 14, marginTop: 12 },
  buttonText: { color: theme.white, fontWeight: '700', textAlign: 'center' }
})
''')

add('mobile/app/volunteer-signup.tsx', '''
import { useState } from 'react'
import { Alert, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native'
import AppScaffold from '../components/AppScaffold'
import { theme } from '../constants/theme'
import { postJson } from '../services/api'

export default function VolunteerSignupScreen() {
  const [form, setForm] = useState({ name: '', email: '', telephone: '', availability: '', travel_courts: '' })

  const submit = async () => {
    try {
      await postJson('/resources/public/volunteer-signup', form)
      Alert.alert('Submitted', 'Volunteer signup received.')
      setForm({ name: '', email: '', telephone: '', availability: '', travel_courts: '' })
    } catch (error: any) {
      Alert.alert('Error', error.message)
    }
  }

  return (
    <AppScaffold title="Volunteer Sign Up">
      <ScrollView contentContainerStyle={styles.form}>
        {Object.keys(form).map((key) => (
          <View key={key}>
            <Text style={styles.label}>{key.replaceAll('_', ' ')}</Text>
            <TextInput style={styles.input} value={(form as any)[key]} onChangeText={(text) => setForm({ ...form, [key]: text })} />
          </View>
        ))}
        <Text style={styles.help}>Courts can include Central, El Cajon, Vista, and Southbay.</Text>
        <TouchableOpacity style={styles.button} onPress={submit}><Text style={styles.buttonText}>Submit</Text></TouchableOpacity>
      </ScrollView>
    </AppScaffold>
  )
}

const styles = StyleSheet.create({
  form: { gap: 12, paddingBottom: 24 },
  label: { fontWeight: '700', color: theme.black, marginBottom: 6 },
  input: { borderWidth: 1, borderColor: theme.line, backgroundColor: theme.white, borderRadius: 12, padding: 14 },
  help: { color: '#444' },
  button: { backgroundColor: theme.black, padding: 16, borderRadius: 14, marginTop: 12 },
  buttonText: { color: theme.white, fontWeight: '700', textAlign: 'center' }
})
''')

for path, content in files.items():
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

print(f'Wrote {len(files)} files')
