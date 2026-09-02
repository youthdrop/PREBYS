from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.deps import get_db, require_admin
from app.models.user import User


router = APIRouter()


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    role: str = 'staff'
    phone: str | None = None
    is_active: bool = True

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = None
    password: str
    role: str = 'staff'
    phone: str | None = None
    is_active: bool = True


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    role: str | None = None
    phone: str | None = None
    is_active: bool | None = None


def clean_role(role: str | None) -> str:
    role = (role or 'staff').strip().lower()
    if role not in {'admin', 'staff', 'volunteer'}:
        raise HTTPException(status_code=400, detail='Role must be admin, staff, or volunteer')
    return role


@router.get('', response_model=list[UserRead])
def list_users(search: str = Query(default=''), admin=Depends(require_admin), db: Session = Depends(get_db)):
    q = db.query(User)
    if search:
        like = f'%{search}%'
        q = q.filter((User.email.ilike(like)) | (User.full_name.ilike(like)))
    return q.order_by(User.full_name.asc().nullslast(), User.email.asc()).all()


@router.post('', response_model=UserRead)
def create_user(payload: UserCreate, admin=Depends(require_admin), db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='A user with that email already exists')

    user = User(
        email=payload.email.lower().strip(),
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=clean_role(payload.role),
        phone=payload.phone,
        is_active=payload.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get('/{user_id}', response_model=UserRead)
def get_user(user_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@router.put('/{user_id}', response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, admin=Depends(require_admin), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    if payload.email is not None:
        new_email = payload.email.lower().strip()
        existing = db.query(User).filter(User.email == new_email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail='A user with that email already exists')
        user.email = new_email

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.password:
        user.password_hash = hash_password(payload.password)
        user.pending_otp = None
        user.pending_otp_expires_at = None
        user.reset_token = None
        user.reset_token_expires_at = None
    if payload.role is not None:
        user.role = clean_role(payload.role)
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete('/{user_id}')
def delete_user(user_id: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    db.delete(user)
    db.commit()
    return {'message': 'User deleted'}
