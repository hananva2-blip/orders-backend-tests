from concurrent.futures import ThreadPoolExecutor

import pytest

from tests.conftest import new_logged_in_user

MOUSE, KEYBOARD, HEADPHONES = 2, 3, 4


def stock(db, product_id):
    return db.execute("SELECT stock FROM products WHERE id = %s", (product_id,)).fetchone()[0]


def test_create_order_updates_db(user, db):
    stock_before = stock(db, MOUSE)

    response = user.post("/orders", json={"product_id": MOUSE, "quantity": 2})
    assert response.status_code == 201
    assert response.json()["total"] == 160.0

    order = db.execute(
        "SELECT user_id, quantity, total FROM orders WHERE id = %s", (response.json()["id"],)
    ).fetchone()
    assert order == (user.user_id, 2, 160)
    assert stock(db, MOUSE) == stock_before - 2


def test_order_more_than_stock_is_rejected(user, db):
    stock_before = stock(db, KEYBOARD)

    response = user.post("/orders", json={"product_id": KEYBOARD, "quantity": stock_before + 1})
    assert response.status_code == 400

    assert stock(db, KEYBOARD) == stock_before
    assert db.execute("SELECT COUNT(*) FROM orders WHERE user_id = %s", (user.user_id,)).fetchone()[0] == 0


def test_order_unknown_product(user):
    response = user.post("/orders", json={"product_id": 999999, "quantity": 1})
    assert response.status_code == 404


@pytest.mark.parametrize("quantity", [0, -1])
def test_order_invalid_quantity(user, quantity):
    response = user.post("/orders", json={"product_id": MOUSE, "quantity": quantity})
    assert response.status_code == 422


def test_order_requires_login(api):
    response = api.post("/orders", json={"product_id": MOUSE, "quantity": 1})
    assert response.status_code == 401


def test_concurrent_orders_do_not_oversell(db):
    """10 users try to buy the last 3 headphones at the same moment."""
    db.execute("UPDATE products SET stock = 3 WHERE id = %s", (HEADPHONES,))
    users = [new_logged_in_user() for _ in range(10)]

    with ThreadPoolExecutor(max_workers=10) as pool:
        codes = list(pool.map(lambda u: u.post("/orders", json={"product_id": HEADPHONES, "quantity": 1}).status_code, users))

    assert codes.count(201) == 3
    assert codes.count(400) == 7
    assert stock(db, HEADPHONES) == 0
