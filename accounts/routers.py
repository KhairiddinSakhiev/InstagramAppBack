from fastapi import Depends, HTTPException, status, Body, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from accounts.models import UserAuth, UserProfile, BlackListToken, EmailVerificationCode, PasswordResetCode
from accounts.schemas import (
    ProfileOut, RegisterRequest, LoginRequest,
    VerifyEmailRequest, ForgetPasswordRequest, ResetPasswordRequest, RegisterResponse
)
from accounts.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    ALGORITHM, SECRET_KEY
)

from accounts.dependencies import get_current_user
from accounts.email import send_verification_code, send_reset_code
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if data.email:
        result = await db.execute(select(UserAuth).filter(UserAuth.email == data.email))
        if result.scalars().first():
            raise HTTPException(status_code=409, detail="Email already exists")

    if data.phone_number:
        result = await db.execute(select(UserAuth).filter(UserAuth.phone_number == data.phone_number))
        if result.scalars().first():
            raise HTTPException(status_code=409, detail="Phone number already exists")

    result = await db.execute(select(UserProfile).filter(UserProfile.username == data.username))
    if result.scalars().first():
        raise HTTPException(status_code=409, detail="Username already exists")

    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    verification_code = EmailVerificationCode(
        email=data.email,
        code=code,
        expires_at=expires_at,
        used=False
    )
    db.add(verification_code)
    await db.commit()

    if data.email:
        success = await send_verification_code(data.email, code)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send verification email")

    password_hash = hash_password(data.password)
    new_auth = UserAuth(email=data.email, phone_number=data.phone_number, hashed_password=password_hash)
    db.add(new_auth)
    await db.flush()

    new_profile = UserProfile(
        user_id=new_auth.id,
        username=data.username,
        full_name=data.full_name,
        birth_date=data.birth_date,
    )
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)

    return {
        "message": "Registration successful! Please check your email for verification code.",
        "email": data.email
    }


@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(EmailVerificationCode).filter(
            EmailVerificationCode.email == data.email,
            EmailVerificationCode.code == data.code,
            EmailVerificationCode.used == False
        )
    )
    verification = result.scalars().first()

    if not verification:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code"
        )

    if datetime.utcnow() > verification.expires_at:
        raise HTTPException(
            status_code=400,
            detail="Verification code has expired. Please request a new one."
        )

    result = await db.execute(select(UserAuth).filter(UserAuth.email == data.email))
    user_auth = result.scalars().first()
    if not user_auth:
        raise HTTPException(status_code=404, detail="User not found")

    user_auth.email_verified = True

    verification.used = True

    await db.commit()

    result = await db.execute(select(UserProfile).filter(UserProfile.user_id == user_auth.id))
    profile = result.scalars().first()

    access_payload = {
        "sub": str(user_auth.id),
        "username": profile.username,
        "type": "access"
    }

    refresh_payload = {
        "sub": str(user_auth.id),
        "username": profile.username,
        "type": "refresh"
    }

    return {
        "message": "Email verified successfully!",
        "access_token": create_access_token(access_payload),
        "refresh_token": create_refresh_token(refresh_payload),
        "token_type": "bearer"
    }


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    query = None
    if data.email:
        result = await db.execute(select(UserAuth).filter(UserAuth.email == data.email))
        query = result.scalars().first()
    elif data.phone_number:
        result = await db.execute(select(UserAuth).filter(UserAuth.phone_number == data.phone_number))
        query = result.scalars().first()

    if not query or not verify_password(data.password, query.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not query.email_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Email not verified. Please check your email for verification code.")

    result = await db.execute(select(UserProfile).filter(UserProfile.user_id == query.id))
    profile = result.scalars().first()

    access_payload = {"sub": str(query.id), "username": profile.username, "type": "access"}
    refresh_payload = {"sub": str(query.id), "username": profile.username, "type": "refresh"}

    return {
        "access_token": create_access_token(access_payload),
        "refresh_token": create_refresh_token(refresh_payload),
        "token_type": "bearer"
    }


@router.get("/me", response_model=ProfileOut)
async def read_user_me(current_user: UserProfile = Depends(get_current_user)):
    return current_user


@router.post("/refresh")
async def refresh_token(refresh_token: str = Body(embed=True), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Use refresh-token")

    result = await db.execute(select(BlackListToken).filter(BlackListToken.token == refresh_token))
    if result.scalars().first():
        raise HTTPException(status_code=401, detail="Token is blacklisted")

    user_id = int(payload["sub"])
    result = await db.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token({"sub": str(user_id), "username": profile.username, "type": "access"})
    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(BlackListToken).filter(BlackListToken.token == token))
    if not result.scalars().first():
        blocked = BlackListToken(token=token)
        db.add(blocked)
        await db.commit()

    return {"message": "Logged Out"}


@router.post("/resend-verification-code")
async def resend_verification_code(data: ForgetPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserAuth).filter(UserAuth.email == data.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    verification_code = EmailVerificationCode(
        email=data.email,
        code=code,
        expires_at=expires_at,
        used=False
    )
    db.add(verification_code)
    await db.commit()

    success = await send_verification_code(data.email, code)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {"message": "Verification code has been resent"}


@router.post("/forget-password")
async def forgot_password(data: ForgetPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserAuth).filter(UserAuth.email == data.email))
    user = result.scalars().first()
    if not user:
        return {"message": "If this email exists, a reset code has been sent"}

    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    reset_code = PasswordResetCode(
        email=data.email,
        code=code,
        expires_at=expires_at,
        used=False
    )
    db.add(reset_code)
    await db.commit()

    success = await send_reset_code(data.email, code)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send reset code")

    return {"message": "If this email exists, a reset code has been sent"}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PasswordResetCode).filter(
            PasswordResetCode.email == data.email,
            PasswordResetCode.code == data.code,
            PasswordResetCode.used == False
        )
    )
    reset_code = result.scalars().first()

    if not reset_code:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    if datetime.utcnow() > reset_code.expires_at:
        raise HTTPException(status_code=400, detail="Reset code has expired. Please request a new one.")

    result = await db.execute(select(UserAuth).filter(UserAuth.email == data.email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(data.new_password)
    reset_code.used = True
    await db.commit()

    return {"message": "Password has been reset successfully"}