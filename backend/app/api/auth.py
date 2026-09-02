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
    return {'id': user.id, 'email': user.email, 'full_name': user.full_name, 'role': user.role, 'is_active': user.is_active}


@router.post('/login')
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail='Invalid email or password')
    if not user.is_active:
        raise HTTPException(status_code=403, detail='This user account is inactive')
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
