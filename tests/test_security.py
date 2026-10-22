import jwt

from tests.conftest import new_logged_in_user


def test_user_cannot_read_other_users_order(user):
    """OWASP API #1 - Broken Object Level Authorization (BOLA)."""
    order_id = user.post("/orders", json={"product_id": 2, "quantity": 1}).json()["id"]
    other_user = new_logged_in_user()

    response = other_user.get(f"/orders/{order_id}")
    assert response.status_code == 403


def test_sql_injection_in_login_is_rejected(api):
    response = api.post("/login", json={"email": "' OR 1=1--@test.com", "password": "' OR '1'='1"})
    assert response.status_code in (401, 422)


def test_forged_token_is_rejected(api, user):
    forged = jwt.encode({"user_id": user.user_id}, "an-attacker-secret-that-is-long-enough", algorithm="HS256")
    response = api.get("/orders/1", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == 401
