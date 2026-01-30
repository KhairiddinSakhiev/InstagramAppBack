from pydantic import BaseModel, EmailStr, ConfigDict, model_validator
from datetime import date
class RegisterRequest(BaseModel):
    email: EmailStr | None = None
    phone_number: str | None = None
    password: str
    confirm_password: str
    full_name: str | None = None
    username: str
    birth_date: date

    model_config = ConfigDict(extra="forbid") 

    @model_validator(mode="after")
    def check_fields_and_passwords(self):
        if not self.email and not self.phone_number:
            raise ValueError("Either email or phone number must be provided")
        
        if self.password != self.confirm_password:
            raise ValueError("Passwords don't match!")
        
        today = date.today()
        age = today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
        if age < 13:
            raise ValueError("You must be at least 13 years old to register")
        
        return self
    
class LoginRequest(BaseModel):
    email: EmailStr | None = None
    phone_number: str | None = None
    password: str

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def check_login_fields(self):
        if not self.email and not self.phone_number:
            raise ValueError("Either email or phone number must be provided")
        return self
    
class ProfileUpdate(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    profile_photo: str | None = None

    model_config = ConfigDict(extra="forbid")
    
class ProfileOut(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    bio: str | None = None
    profile_photo: str | None = None

    class Config:
        from_attributes = True