CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    stock INT NOT NULL CHECK (stock >= 0)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    product_id INT NOT NULL REFERENCES products(id),
    quantity INT NOT NULL,
    total NUMERIC(10, 2) NOT NULL
);

INSERT INTO products (name, price, stock) VALUES
    ('Laptop', 3500.00, 1000),
    ('Mouse', 80.00, 1000),
    ('Keyboard', 250.00, 1000),
    ('Limited Edition Headphones', 900.00, 3);
