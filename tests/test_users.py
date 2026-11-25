import uuid

import pytest

from tests.conftest import PASSWORD


def test_register_saves_user_in_db(api, db):
    email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    response = api.post("/users", json={"email": email, "password": PASSWORD})
    assert response.status_code == 201

    password_hash = db.execute("SELECT password_hash FROM users WHERE email = %s", (email,)).fetchone()[0]
    assert PASSWORD not in password_hash  # never store plain passwords
    salt, digest = password_hash.split("$")
    assert len(salt) == 32 and len(digest) == 64


def test_same_password_gets_different_hashes(api, db):
    emails = [f"user_{uuid.uuid4().hex[:8]}@test.com" for _ in range(2)]
    for email in emails:
        api.post("/users", json={"email": email, "password": PASSWORD})

    hashes = db.execute("SELECT password_hash FROM users WHERE email = ANY(%s)", (emails,)).fetchall()
    assert hashes[0] != hashes[1]  # a random salt per user


def test_register_duplicate_email(api, user):
    response = api.post("/users", json={"email": user.email, "password": PASSWORD})
    assert response.status_code == 409


@pytest.mark.parametrize("email, password", [
    ("not-an-email", PASSWORD),
    ("valid@test.com", "short"),
    ("", ""),
])
def test_register_invalid_input(api, email, password):
    response = api.post("/users", json={"email": email, "password": password})
    assert response.status_code == 422


def test_login_wrong_password(api, user):
    response = api.post("/login", json={"email": user.email, "password": "WrongPassw0rd"})
    assert response.status_code == 401
