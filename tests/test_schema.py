from pydantic import BaseModel, Field


class Product(BaseModel):
    id: int
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class Order(BaseModel):
    id: int
    product_id: int
    quantity: int = Field(gt=0)
    total: float = Field(gt=0)


def test_products_schema(api):
    products = api.get("/products").json()
    assert products
    for product in products:
        Product.model_validate(product)


def test_order_schema(user):
    order_id = user.post("/orders", json={"product_id": 2, "quantity": 1}).json()["id"]
    Order.model_validate(user.get(f"/orders/{order_id}").json())
