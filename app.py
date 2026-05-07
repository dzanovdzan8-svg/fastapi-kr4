from fastapi import FastAPI, Cookie, Request, Response, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import time
import hmac
import hashlib
from models import UserCreate, Product, sample_products

app = FastAPI(
    title="Bookstore API",
    description="API для управления каталогом книг и аутентификации пользователей",
)

USERS_DB = {
    "mihail": "secure1234",
    "admin": "adminpass"
}
active_sessions = {}
TOKEN_SECRET = "bookstore_secret_key_7x9"
SESSION_TTL = 300
SESSION_RENEW_AFTER = 180

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/create_user")
def create_user(user: UserCreate):
    if user.age is not None and user.age <= 0:
        raise HTTPException(status_code=400, detail="Возраст должен быть положительным числом")
    return user

@app.get("/products/search")
def search_products(keyword: str, category: Optional[str] = None, limit: int = 10):
    result = []
    for p in sample_products:
        if keyword.lower() in p.name.lower():
            if category is None or p.category.lower() == category.lower():
                result.append(p)
    return result[:limit]

@app.get("/product/{product_id}")
def get_product(product_id: int):
    for p in sample_products:
        if p.product_id == product_id:
            return p
    raise HTTPException(status_code=404, detail="Товар не найден")

class CommonHeaders(BaseModel):
    user_agent: str = Header(alias="User-Agent")
    accept_language: str = Header(alias="Accept-Language")

@app.post("/login")
def login(data: LoginRequest, response: Response):
    if data.username not in USERS_DB or USERS_DB[data.username] != data.password:
        raise HTTPException(status_code=401, detail="Неверные учётные данные")
    token = str(uuid.uuid4())
    active_sessions[token] = data.username
    response.set_cookie(key="session_token", value=token, httponly=True)
    return {"message": "Аутентификация прошла успешно"}

@app.get("/user")
def get_user(session_token: Optional[str] = Cookie(default=None)):
    if session_token is None or session_token not in active_sessions:
        return JSONResponse(status_code=401, content={"message": "Сессия не найдена или недействительна"})
    username = active_sessions[session_token]
    return {"username": username, "email": f"{username}@bookstore.ru"}

def compute_hmac(value: str) -> str:
    return hmac.new(TOKEN_SECRET.encode(), value.encode(), hashlib.sha256).hexdigest()

def build_token(user_id: str) -> str:
    return f"{user_id}.{compute_hmac(user_id)}"

def validate_token(token: str) -> Optional[str]:
    parts = token.split(".")
    if len(parts) != 2:
        return None
    user_id, signature = parts
    if compute_hmac(user_id) != signature:
        return None
    return user_id

@app.post("/login_signed")
def login_signed(data: LoginRequest, response: Response):
    if data.username not in USERS_DB or USERS_DB[data.username] != data.password:
        raise HTTPException(status_code=401, detail="Неверные учётные данные")
    token = build_token(str(uuid.uuid4()))
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=3600)
    return {"message": "Аутентификация прошла успешно"}

@app.get("/profile")
def get_profile(session_token: Optional[str] = Cookie(default=None)):
    if session_token is None:
        return JSONResponse(status_code=401, content={"message": "Токен отсутствует"})
    user_id = validate_token(session_token)
    if user_id is None:
        return JSONResponse(status_code=401, content={"message": "Токен недействителен"})
    return {"user_id": user_id, "email": "user@bookstore.ru"}

def build_expiring_token(user_id: str, ts: int) -> str:
    payload = f"{user_id}.{ts}"
    sig = hmac.new(TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"

def validate_expiring_token(token: str):
    parts = token.split(".")
    if len(parts) != 3:
        return None, None
    user_id, ts_str, sig = parts
    payload = f"{user_id}.{ts_str}"
    if hmac.new(TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest() != sig:
        return None, None
    return user_id, int(ts_str)

@app.post("/login_advanced")
def login_advanced(data: LoginRequest, response: Response):
    if data.username not in USERS_DB or USERS_DB[data.username] != data.password:
        raise HTTPException(status_code=401, detail="Неверные учётные данные")
    token = build_expiring_token(str(uuid.uuid4()), int(time.time()))
    response.set_cookie(key="session_token", value=token, httponly=True, secure=False, max_age=SESSION_TTL)
    return {"message": "Аутентификация прошла успешно"}

@app.get("/profile_advanced")
def get_profile_advanced(session_token: Optional[str] = Cookie(default=None), response: Response):
    if session_token is None:
        return JSONResponse(status_code=401, content={"message": "Токен отсутствует"})
    user_id, issued_at = validate_expiring_token(session_token)
    if user_id is None:
        return JSONResponse(status_code=401, content={"message": "Токен недействителен"})

    elapsed = int(time.time()) - issued_at

    if elapsed >= SESSION_TTL:
        return JSONResponse(status_code=401, content={"message": "Сессия истекла, войдите снова"})

    if elapsed >= SESSION_RENEW_AFTER:
        new_token = build_expiring_token(user_id, int(time.time()))
        response.set_cookie(key="session_token", value=new_token, httponly=True, secure=False, max_age=SESSION_TTL)

    return {"user_id": user_id, "email": "user@bookstore.ru"}

@app.get("/headers")
def get_headers(headers: CommonHeaders = Header()):
    return {"User-Agent": headers.user_agent, "Accept-Language": headers.accept_language}

@app.get("/info")
def get_info(request: Request, headers: CommonHeaders = Header(), response: Response):
    response.headers["X-Server-Time"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "client_ip": request.client.host,
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language,
        },
    }
