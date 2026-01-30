from database import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Date
from datetime import date

class UserAuth(BaseModel):
    
    email: Mapped[str | None] = mapped_column(String(100), unique=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))

    profile: Mapped["UserProfile"] = relationship(back_populates="auth", uselist=False)


class UserProfile(BaseModel):
    
    user_id: Mapped[int] = mapped_column(ForeignKey("user_auth.id"), unique=True)

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(Text)
    birth_date: Mapped[date] = mapped_column(Date)
    profile_photo: Mapped[str | None] = mapped_column(String(300))
    
    auth: Mapped[UserAuth] = relationship(back_populates="profile")