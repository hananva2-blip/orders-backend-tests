# Orders API – Backend Test Automation

[![tests](https://github.com/hananva2-blip/orders-backend-tests/actions/workflows/tests.yml/badge.svg)](https://github.com/hananva2-blip/orders-backend-tests/actions/workflows/tests.yml)

Backend tests for a small orders service (FastAPI + PostgreSQL).
The tests check the **API and the database together**: every action is verified both in the response and in the tables.

**Stack:** Python · pytest · requests · PostgreSQL (psycopg) · pydantic · Locust · Docker Compose · GitHub Actions

## What is tested
| Area | Examples |
|---|---|
| **API + DB** | An order returns 201 **and** the row is saved **and** stock goes down |
| **Business rules** | Ordering more than the stock is rejected and nothing changes in the DB |
| **Concurrency** | 10 users buy the last 3 items at the same moment – exactly 3 succeed, no overselling |
| **Validation** | Bad email, short password, quantity 0 / -1 → 422 |
| **Security (OWASP API Top 10)** | A user can't read another user's order (BOLA → 403), forged JWT → 401, SQL injection in login fails, passwords are stored hashed |
| **Contract** | Responses match pydantic schemas |
| **Performance** | Locust load test: 20 users, fails on any error |

## Project structure
```
app/                 The service under test (FastAPI + init.sql)
tests/
  conftest.py        Api session, logged-in user, DB connection
  test_users.py      Register, duplicate, validation, login
  test_orders.py     Orders, stock, concurrency
  test_security.py   BOLA, forged token, SQL injection
  test_schema.py     Response contracts
locustfile.py        Load test
```

## Run locally
```bash
docker compose up -d --build --wait     # API on :8000, PostgreSQL on :5433
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
locust -f locustfile.py --headless -u 20 -r 10 -t 30s --host http://localhost:8000
```
API docs (Swagger): http://localhost:8000/docs
