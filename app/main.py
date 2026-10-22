import hashlib
import os

import jwt
import psycopg
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field

DB_URL = os.getenv("DB_URL", "postgresql://shop:shop@localhost:5433/shop")
SECRET = os.getenv("JWT_SECRET", "local-dev-secret-change-me-in-production")

app = FastAPI(title="Orders API")


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class OrderRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


def db():
    with psycopg.connect(DB_URL) as conn:
        yield conn


def hash_password(password):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), SECRET.encode(), 100_000).hex()


def current_user(authorization: str = Header(None)):
    try:
        return jwt.decode(authorization.removeprefix("Bearer "), SECRET, algorithms=["HS256"])["user_id"]
    except Exception:
        raise HTTPException(401, "Not authenticated")


@app.post("/users", status_code=201)
def register(body: Credentials, conn=Depends(db)):
    try:
        row = conn.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
            (body.email, hash_password(body.password)),
        ).fetchone()
    except psycopg.errors.UniqueViolation:
        raise HTTPException(409, "Email already exists")
    return {"id": row[0], "email": body.email}


@app.post("/login")
def login(body: Credentials, conn=Depends(db)):
    row = conn.execute(
        "SELECT id FROM users WHERE email = %s AND password_hash = %s",
        (body.email, hash_password(body.password)),
    ).fetchone()
    if not row:
        raise HTTPException(401, "Invalid email or password")
    return {"token": jwt.encode({"user_id": row[0]}, SECRET, algorithm="HS256")}


@app.get("/products")
def products(conn=Depends(db)):
    rows = conn.execute("SELECT id, name, price, stock FROM products ORDER BY id").fetchall()
    return [{"id": r[0], "name": r[1], "price": float(r[2]), "stock": r[3]} for r in rows]


@app.post("/orders", status_code=201)
def create_order(body: OrderRequest, user_id=Depends(current_user), conn=Depends(db)):
    # Lock the product row so two orders can't take the same stock
    product = conn.execute(
        "SELECT price, stock FROM products WHERE id = %s FOR UPDATE", (body.product_id,)
    ).fetchone()
    if not product:
        raise HTTPException(404, "Product not found")
    if product[1] < body.quantity:
        raise HTTPException(400, "Not enough stock")
    conn.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (body.quantity, body.product_id))
    total = product[0] * body.quantity
    order_id = conn.execute(
        "INSERT INTO orders (user_id, product_id, quantity, total) VALUES (%s, %s, %s, %s) RETURNING id",
        (user_id, body.product_id, body.quantity, total),
    ).fetchone()[0]
    return {"id": order_id, "product_id": body.product_id, "quantity": body.quantity, "total": float(total)}


@app.get("/orders/{order_id}")
def get_order(order_id: int, user_id=Depends(current_user), conn=Depends(db)):
    row = conn.execute(
        "SELECT id, user_id, product_id, quantity, total FROM orders WHERE id = %s", (order_id,)
    ).fetchone()
    if not row:
        raise HTTPException(404, "Order not found")
    if row[1] != user_id:
        raise HTTPException(403, "Not your order")
    return {"id": row[0], "product_id": row[2], "quantity": row[3], "total": float(row[4])}
