import uuid

from locust import HttpUser, between, task

PASSWORD = "Passw0rd!"
USB_CABLE = 5  # Its own product with a huge stock (init.sql), so load runs don't drain the test data


class Shopper(HttpUser):
    wait_time = between(0.5, 1)

    def on_start(self):
        email = f"load_{uuid.uuid4().hex[:8]}@test.com"
        self.client.post("/users", json={"email": email, "password": PASSWORD})
        token = self.client.post("/login", json={"email": email, "password": PASSWORD}).json()["token"]
        self.client.headers["Authorization"] = f"Bearer {token}"

    @task(3)
    def browse_products(self):
        self.client.get("/products")

    @task(1)
    def buy_cable(self):
        self.client.post("/orders", json={"product_id": USB_CABLE, "quantity": 1})
