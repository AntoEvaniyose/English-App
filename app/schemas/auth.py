
from pydantic import BaseModel, field_validator,Field, EmailStr
from app.utils import validate_email
from app.utils import validate_password


class AdminCreate(BaseModel):
    name: str = Field(..., example="Admin Name",min_length=3, max_length=50)
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_validator(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def password_validator(cls, v):
        return validate_password(v)    
    

class AdminLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_validator(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def password_validator(cls, v):
        return validate_password(v) 


class AdminOTP(BaseModel):
    email: str
    otp: int = Field(..., example=123456, ge=100000, le=999999,check_fields=False)

    @field_validator("email")
    @classmethod
    def email_validator(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v
    

class UserOTP(BaseModel):
    email: str
    otp: int = Field(..., example=123456, ge=100000, le=999999,check_fields=False)

    @field_validator("email")
    @classmethod
    def email_validator(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v    


class RegisterRequest(BaseModel):
    name: str = Field(..., example="User Name",min_length=3, max_length=50)
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_validator(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def password_validator(cls, v):
        return validate_password(v)

class TokenRefreshRequest(BaseModel):
    refresh_token: str    

class UserLoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_validator(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def password_validator(cls, v):
        return validate_password(v)    
    

class GoogleAuthRequest(BaseModel):
    id_token: str    

class ResendOTPRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def email_validator(cls, v):
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v

class AdminForgotPasswordSchema(BaseModel):
    email: EmailStr

class AdminResetPasswordSchema(BaseModel):
    uid: str
    token: str
    new_password: str
    confirm_password: str


class UserForgotPasswordSchema(BaseModel):
    email: EmailStr

class UserResetPasswordSchema(BaseModel):
    uid: str
    token: str
    new_password: str
    confirm_password: str