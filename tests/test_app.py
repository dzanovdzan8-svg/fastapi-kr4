import pytest
import httpx
from faker import Faker
from app import app
from database import get_db

fake = Faker()

def clear_db():
    db = get_db()
    db.execute("DELETE FROM users")
    db.execute("DELETE FROM products")
    db.commit()
    db.close()

@pytest.fixture(autouse=True)
def cleanup():
    clear_db()
    yield
    clear_db()

@pytest.mark.asyncio
async def test_create_user():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/users", json={
            "username": fake.user_name(), "age": 25, "email": fake.email(),
            "password": "securePass1", "phone": "+79991234567"
        })
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["username"] != ""

@pytest.mark.asyncio
async def test_get_user():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/users", json={"username": "test", "age": 20, "email": "t@t.ru", "password": "12345678"})
        res = await client.get("/users/1")
        assert res.status_code == 200
        assert res.json()["username"] == "test"

@pytest.mark.asyncio
async def test_get_missing_user():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/users/999")
        assert res.status_code == 404

@pytest.mark.asyncio
async def test_delete_user():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/users", json={"username": "del", "age": 22, "email": "d@d.ru", "password": "12345678"})
        res = await client.delete("/users/1")
        assert res.status_code == 204
        res2 = await client.get("/users/1")
        assert res2.status_code == 404
