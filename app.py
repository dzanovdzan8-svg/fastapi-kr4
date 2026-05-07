from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from models import UserCreate, UserOut, ErrorResponse, ProductCreate, ProductOut
from database import get_db, init_db

app = FastAPI(title="KR4 API")

class CustomAuthError(Exception):
    status_code = 401
    message = "Authentication failed"

class CustomResourceError(Exception):
    status_code = 404
    message = "Resource not found"

@app.exception_handler(CustomAuthError)
async def auth_handler(request: Request, exc: CustomAuthError):
    return JSONResponse(status_code=exc.status_code, content=exc.message)

@app.exception_handler(CustomResourceError)
async def resource_handler(request: Request, exc: CustomResourceError):
    return JSONResponse(status_code=exc.status_code, content=exc.message)

@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    errors = []
    for err in exc.errors():
        errors.append(f"{err['loc'][-1]}: {err['msg']}")
    return JSONResponse(
        status_code=400,
        content={"status_code": 400, "message": "Validation error", "details": "; ".join(errors)}
    )

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserCreate):
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO users (username, age, email, phone) VALUES (?, ?, ?, ?)",
            (user.username, user.age, user.email, user.phone)
        )
        db.commit()
        return {"id": cursor.lastrowid, **user.model_dump()}
    except Exception as e:
        raise CustomAuthError()
    finally:
        db.close()

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    if row is None:
        raise CustomResourceError()
    return dict(row)

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    db = get_db()
    res = db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    db.close()
    if res.rowcount == 0:
        raise CustomResourceError()
    return None

@app.post("/products", response_model=ProductOut, status_code=201)
def create_product(product: ProductCreate):
    db = get_db()
    cur = db.execute("INSERT INTO products (title, price, count) VALUES (?, ?, ?)", 
                     (product.title, product.price, product.count))
    db.commit()
    db.close()
    return {"id": cur.lastrowid, **product.model_dump(), "description": None}

@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int):
    db = get_db()
    row = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    db.close()
    if row is None:
        raise CustomResourceError()
    return dict(row)

@app.on_event("startup")
def startup():
    init_db()
