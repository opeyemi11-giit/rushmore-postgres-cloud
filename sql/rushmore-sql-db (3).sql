-- The DB Table Creation

-- Stores Table
create table stores (
	store_id serial primary key,
	address VARCHAR(255) NOT NULL, --The street address,
	city VARCHAR(100) NOT NULL, --The city of the store.
	phone_number VARCHAR(20) UNIQUE NOT NULL, --The store's main phone number.
	opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP --When the store opened.
);

-- Customers Table
create table customers (
	customer_id SERIAL PRIMARY KEY, --Unique ID for the customer.
	first_name VARCHAR(100) NOT NULL, --Customer's first name.
	last_name VARCHAR(100) NOT NULL, --Customer's last name.
	email VARCHAR(255) UNIQUE NOT NULL, --Customer's email (for logins, receipts).
	phone_number VARCHAR(30) UNIQUE NOT NULL, --Customer's phone (for order updates).
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP --When the customer account was created.


);


-- Ingredients Table
create table ingredients (
	ingredient_id SERIAL PRIMARY KEY, --Unique ID for the ingredient.
	name VARCHAR(100) UNIQUE NOT NULL, --e.g., "Pepperoni", "Mozzarella Cheese", "Pizza Dough".
	stock_quantity NUMERIC(10, 2) NOT NULL DEFAULT 0, --Current amount in stock.
	unit VARCHAR(20) NOT NULL --The unit of measure for stock_quantity (e.g., 'kg', 'liters', 'units').
);

-- Menu Items Table
create table menu_items (
	item_id SERIAL PRIMARY KEY, --Unique ID for the menu item.
	name VARCHAR(150) NOT NULL, --e.g., "Large Pepperoni Pizza".
	category VARCHAR(50) NOT NULL, --e.g., 'Pizza', 'Drink', 'Side'.
	size VARCHAR(20), --e.g., 'Small', 'Medium', 'Large', '500ml', 'N/A'.
	price NUMERIC(10,2)


);


-- Orders Table
create table orders (
	order_id SERIAL PRIMARY KEY, --Unique ID for the order.
	customer_id INTEGER REFERENCES Customers(customer_id) ON DELETE SET NULL, --Foreign Key to Customers. (Set NULL on delete so order history remains if a customer account is deleted).
	store_id INTEGER REFERENCES Stores(store_id) ON DELETE RESTRICT, --Foreign Key to Stores. (Restrict delete to prevent orphaning order data).
	order_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, --When the order was placed.
	total_amount NUMERIC(10, 2) NOT NULL -- The final calculated total for the order.
);

-- Orders Items
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES menu_items(item_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);


