from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from accounts.models import UserAuth, UserProfile
from accounts.schemas import ProfileOut, RegisterRequest
from accounts.security import hash_password
from database import get_db 

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if data.email:
        result = await db.execute(select(UserAuth).filter(UserAuth.email == data.email))
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")

    if data.phone_number:
        result = await db.execute(select(UserAuth).filter(UserAuth.phone_number == data.phone_number))
        existing_phone = result.scalars().first()
        if existing_phone:
            raise HTTPException(status_code=400, detail="Phone number already exists")

    result = await db.execute(select(UserProfile).filter(UserProfile.username == data.username))
    existing_username = result.scalars().first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    password_hash = hash_password(data.password)

    new_auth = UserAuth(
        email=data.email,
        phone_number=data.phone_number,
        hashed_password=password_hash,
    )
    db.add(new_auth)
    await db.commit()
    await db.refresh(new_auth)

    new_profile = UserProfile(
        user_id=new_auth.id,
        username=data.username,
        full_name=data.full_name,
        birth_date=data.birth_date,
        profile_photo=None,
        bio=None,
    )
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)

    return new_profile