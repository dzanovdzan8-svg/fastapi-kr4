from pydantic import BaseModel, EmailStr, constr, conint
from typing import Optional

class UserCreate(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    age: int
    email: str
    phone: Optional[str]

class ErrorResponse(BaseModel):
    status_code: int
    message: str
    details: Optional[str] = None

class ProductCreate(BaseModel):
    title: str
    price: float
    count: int

class ProductOut(ProductCreate):
    id: int
    description: Optional[str] = None
