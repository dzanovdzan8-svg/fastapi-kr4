from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
    is_subscribed: Optional[bool] = None

class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float

sample_products = [
    Product(product_id=1, name="Чистый код", category="Программирование", price=850.0),
    Product(product_id=2, name="Паттерны проектирования", category="Программирование", price=1200.0),
    Product(product_id=3, name="Алгоритмы. Построение и анализ", category="Алгоритмы", price=2100.0),
    Product(product_id=4, name="Прагматичный программист", category="Программирование", price=950.0),
    Product(product_id=5, name="Введение в алгоритмы", category="Алгоритмы", price=1750.0),
]
