from database import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Date
from datetime import datetime, date


class UserAuth(BaseModel):
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)

    email_verified: Mapped[bool] = mapped_column(default=False)

    profile: Mapped["UserProfile"] = relationship(back_populates="auth", uselist=False)


class UserProfile(BaseModel):
    user_id: Mapped[int] = mapped_column(ForeignKey("userauths.id"), unique=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    profile_photo: Mapped[str | None] = mapped_column(String(300))

    auth: Mapped[UserAuth] = relationship(back_populates="profile")


class EmailVerificationCode(BaseModel):
    email: Mapped[str] = mapped_column(String(100), index=True)  # исправлено: было int
    code: Mapped[str] = mapped_column(String(6))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column()
    used: Mapped[bool] = mapped_column(default=False)


class PasswordResetCode(BaseModel):
    email: Mapped[str] = mapped_column(String(100), index=True)
    code: Mapped[str] = mapped_column(String(6))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column()
    used: Mapped[bool] = mapped_column(default=False)


class BlackListToken(BaseModel):
    token: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)