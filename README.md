# Контрольная работа 2

## Запуск
pip install -r requirements.txt
uvicorn app:app --reload

## Тестирование
curl -X POST http://127.0.0.1:8000/create_user -H "Content-Type: application/json" -d '{"name":"Test","email":"test@mail.ru","age":25}'

curl "http://127.0.0.1:8000/products/search?keyword=код"

curl -c cookies.txt -X POST http://127.0.0.1:8000/login -H "Content-Type: application/json" -d '{"username":"mihail","password":"secure1234"}'
curl -b cookies.txt http://127.0.0.1:8000/user

curl -c cookies.txt -X POST http://127.0.0.1:8000/login_signed -H "Content-Type: application/json" -d '{"username":"admin","password":"adminpass"}'
curl -b cookies.txt http://127.0.0.1:8000/profile

curl -c cookies.txt -X POST http://127.0.0.1:8000/login_advanced -H "Content-Type: application/json" -d '{"username":"mihail","password":"secure1234"}'
curl -b cookies.txt http://127.0.0.1:8000/profile_advanced

curl -H "User-Agent: TestClient" -H "Accept-Language: ru" http://127.0.0.1:8000/headers
curl -H "User-Agent: TestClient" -H "Accept-Language: ru" http://127.0.0.1:8000/info
