import uuid

import psycopg
import pytest
import requests

API_URL = "http://localhost:8000"
DB_URL = "postgresql://shop:shop@localhost:5433/shop"
PASSWORD = "Passw0rd!"


class Api(requests.Session):
    """requests.Session that only needs the path, e.g. api.get("/products")."""

    def request(self, method, path, **kwargs):
        return super().request(method, API_URL + path, **kwargs)


def new_logged_in_user():
    """Registers a unique user and returns an Api session that is already logged in."""
    api = Api()
    api.email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    api.user_id = api.post("/users", json={"email": api.email, "password": PASSWORD}).json()["id"]
    token = api.post("/login", json={"email": api.email, "password": PASSWORD}).json()["token"]
    api.headers["Authorization"] = f"Bearer {token}"
    return api


@pytest.fixture
def api():
    return Api()


@pytest.fixture
def user():
    return new_logged_in_user()


@pytest.fixture
def db():
    with psycopg.connect(DB_URL, autocommit=True) as conn:
        yield conn
