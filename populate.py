import random
from decimal import Decimal
from pathlib import Path

import yaml
import psycopg2
from faker import Faker
from psycopg2.extras import execute_values


# --------------------------------------------------
# Basic setup
# --------------------------------------------------

fake = Faker()

# This helps Python find config.yaml from the project root,
# even if this file is inside the scripts folder.
PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"


# --------------------------------------------------
# Load database configuration from config.yaml
# --------------------------------------------------

def load_config():
    """
    Reads database connection details from config.yaml.
    """

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"config.yaml was not found at: {CONFIG_FILE}"
        )

    with open(CONFIG_FILE, "r") as file:
        config = yaml.safe_load(file)

    if "database" not in config:
        raise ValueError("config.yaml must contain a 'database' section.")

    return config["database"]


# --------------------------------------------------
# Connect to PostgreSQL database
# --------------------------------------------------

def get_connection():
    """
    Creates a connection to the PostgreSQL database.
    """

    db_config = load_config()

    connection = psycopg2.connect(
        host=db_config["host"],
        port=db_config["port"],
        dbname=db_config["name"],
        user=db_config["user"],
        password=db_config["password"],
        sslmode=db_config.get("sslmode", "require")
    )

    return connection


# --------------------------------------------------
# Clear existing data
# --------------------------------------------------

def clear_existing_data(cursor):
    """
    Deletes existing data from the tables.

    RESTART IDENTITY resets the SERIAL IDs back to 1.
    CASCADE handles foreign key relationships.
    """

    cursor.execute("""
        TRUNCATE TABLE
            order_items,
            orders,
            customers,
            menu_items,
            ingredients,
            stores
        RESTART IDENTITY CASCADE;
    """)

    print("Existing data cleared successfully.")


# --------------------------------------------------
# Insert stores
# --------------------------------------------------

def insert_stores(cursor):
    """
    Inserts 5 pizzeria store locations.
    """

    stores = [
        ("37 Camden High Street", "London", "07123456701"),
        ("82 Deansgate", "Manchester", "07123456702"),
        ("14 Park Row", "Leeds", "07123456703"),
        ("56 Bold Street", "Liverpool", "07123456704"),
        ("23 Queen Street", "Cardiff", "07123456705"),
    ]

    query = """
        INSERT INTO stores (address, city, phone_number)
        VALUES %s
        RETURNING store_id;
    """

    execute_values(cursor, query, stores)

    cursor.execute("SELECT store_id FROM stores;")
    rows = cursor.fetchall()

    store_ids = []

    for row in rows:
        store_ids.append(row[0])

    print(f"Inserted {len(store_ids)} stores.")

    return store_ids


# --------------------------------------------------
# Insert ingredients
# --------------------------------------------------

def insert_ingredients(cursor):
    """
    Inserts ingredients used by the pizzeria.
    """

    ingredient_names = [
        "Pizza Dough",
        "Tomato Sauce",
        "Mozzarella Cheese",
        "Cheddar Cheese",
        "Pepperoni",
        "Chicken",
        "Beef",
        "Sausage",
        "Bacon",
        "Ham",
        "Mushrooms",
        "Onions",
        "Green Peppers",
        "Red Peppers",
        "Black Olives",
        "Sweet Corn",
        "Pineapple",
        "Jalapenos",
        "Garlic",
        "Basil",
        "Oregano",
        "Olive Oil",
        "BBQ Sauce",
        "Hot Sauce",
        "Ranch Sauce",
        "Spinach",
        "Fresh Tomatoes",
        "Parmesan Cheese",
        "Feta Cheese",
        "Tuna",
        "Shrimp",
        "Lettuce",
        "Cucumber",
        "Mayonnaise",
        "Ketchup",
        "Potatoes",
        "Bread",
        "Butter",
        "Flour",
        "Yeast",
        "Salt",
        "Sugar",
        "Bottled Water",
        "Coca-Cola Syrup",
        "Orange Syrup",
        "Ice Cream Mix",
        "Chocolate Sauce",
        "Vanilla Extract",
        "Milk",
        "Eggs"
    ]

    ingredients = []

    for name in ingredient_names:
        stock_quantity = round(random.uniform(20, 500), 2)
        unit = random.choice(["kg", "liters", "units"])

        ingredients.append((name, stock_quantity, unit))

    query = """
        INSERT INTO ingredients (name, stock_quantity, unit)
        VALUES %s
        RETURNING ingredient_id;
    """

    execute_values(cursor, query, ingredients)

    cursor.execute("SELECT ingredient_id FROM ingredients;")
    rows = cursor.fetchall()

    ingredient_ids = []

    for row in rows:
        ingredient_ids.append(row[0])

    print(f"Inserted {len(ingredient_ids)} ingredients.")

    return ingredient_ids


# --------------------------------------------------
# Insert menu items
# --------------------------------------------------

def insert_menu_items(cursor):
    """
    Inserts menu items and their prices.

    This function returns a dictionary like:
    {
        1: Decimal("3500.00"),
        2: Decimal("5000.00")
    }

    That dictionary will be used later when creating orders.
    """

    menu_items = [
        ("Small Margherita Pizza", "Pizza", "Small", 3500),
        ("Medium Margherita Pizza", "Pizza", "Medium", 5000),
        ("Large Margherita Pizza", "Pizza", "Large", 7000),

        ("Small Pepperoni Pizza", "Pizza", "Small", 4200),
        ("Medium Pepperoni Pizza", "Pizza", "Medium", 6200),
        ("Large Pepperoni Pizza", "Pizza", "Large", 8500),

        ("Small BBQ Chicken Pizza", "Pizza", "Small", 4500),
        ("Medium BBQ Chicken Pizza", "Pizza", "Medium", 6500),
        ("Large BBQ Chicken Pizza", "Pizza", "Large", 9000),

        ("Small Meat Lovers Pizza", "Pizza", "Small", 5000),
        ("Medium Meat Lovers Pizza", "Pizza", "Medium", 7500),
        ("Large Meat Lovers Pizza", "Pizza", "Large", 10000),

        ("Small Veggie Supreme Pizza", "Pizza", "Small", 4000),
        ("Medium Veggie Supreme Pizza", "Pizza", "Medium", 6000),
        ("Large Veggie Supreme Pizza", "Pizza", "Large", 8000),

        ("Garlic Bread", "Side", "Regular", 2000),
        ("Chicken Wings", "Side", "6 Pieces", 4500),
        ("Potato Wedges", "Side", "Regular", 2500),
        ("Cheesy Breadsticks", "Side", "Regular", 3000),

        ("Coca-Cola", "Drink", "500ml", 800),
        ("Sprite", "Drink", "500ml", 800),
        ("Fanta", "Drink", "500ml", 800),
        ("Bottled Water", "Drink", "500ml", 500),

        ("Chocolate Ice Cream", "Dessert", "Cup", 1500),
        ("Vanilla Ice Cream", "Dessert", "Cup", 1500),
    ]

    query = """
        INSERT INTO menu_items (name, category, size, price)
        VALUES %s
        RETURNING item_id, price;
    """

    execute_values(cursor, query, menu_items)

    cursor.execute("SELECT item_id, price FROM menu_items;")
    rows = cursor.fetchall()

    menu_item_prices = {}

    for row in rows:
        item_id = row[0]
        price = row[1]
        menu_item_prices[item_id] = Decimal(price)

    print(f"Inserted {len(menu_item_prices)} menu items.")

    return menu_item_prices


# --------------------------------------------------
# Insert customers
# --------------------------------------------------

def insert_customers(cursor, number_of_customers=1200):
    """
    Inserts fake customers using Faker.
    """

    customers = []

    for _ in range(number_of_customers):
        first_name = fake.first_name()
        last_name = fake.last_name()

        # Faker's unique helps avoid duplicate emails and phone numbers.
        email = fake.unique.email()
        phone_number = fake.unique.phone_number()

        created_at = fake.date_time_this_year()

        customers.append((
            first_name,
            last_name,
            email,
            phone_number,
            created_at
        ))

    query = """
        INSERT INTO customers
            (first_name, last_name, email, phone_number, created_at)
        VALUES %s
        RETURNING customer_id;
    """

    execute_values(cursor, query, customers)

    cursor.execute("SELECT customer_id FROM customers;")
    rows = cursor.fetchall()

    customer_ids = []

    for row in rows:
        customer_ids.append(row[0])

    print(f"Inserted {len(customer_ids)} customers.")

    return customer_ids


# --------------------------------------------------
# Insert orders and order items
# --------------------------------------------------

def insert_orders_and_order_items(
    cursor,
    customer_ids,
    store_ids,
    menu_item_prices,
    number_of_orders=5500
):
    """
    Inserts orders and the items inside each order.

    One order can have many order items.
    Example:
        Order 1:
            - 1 Large Pepperoni Pizza
            - 2 Coca-Cola
            - 1 Garlic Bread
    """

    menu_item_ids = list(menu_item_prices.keys())

    total_order_items_inserted = 0

    for order_number in range(1, number_of_orders + 1):

        customer_id = random.choice(customer_ids)
        store_id = random.choice(store_ids)
        order_timestamp = fake.date_time_this_year()

        # Each order will have between 1 and 5 different item lines.
        number_of_items_in_order = random.randint(1, 5)

        order_items_for_this_order = []
        total_amount = Decimal("0.00")

        for _ in range(number_of_items_in_order):
            item_id = random.choice(menu_item_ids)
            quantity = random.randint(1, 4)
            unit_price = menu_item_prices[item_id]

            line_total = unit_price * quantity
            total_amount = total_amount + line_total

            order_items_for_this_order.append((
                item_id,
                quantity,
                unit_price
            ))

        # Insert one row into orders first.
        cursor.execute("""
            INSERT INTO orders
                (customer_id, store_id, order_timestamp, total_amount)
            VALUES
                (%s, %s, %s, %s)
            RETURNING order_id;
        """, (
            customer_id,
            store_id,
            order_timestamp,
            total_amount
        ))

        order_id = cursor.fetchone()[0]

        # Now insert the items for that order into order_items.
        order_item_rows = []

        for item in order_items_for_this_order:
            item_id = item[0]
            quantity = item[1]
            unit_price = item[2]

            order_item_rows.append((
                order_id,
                item_id,
                quantity,
                unit_price
            ))

        query = """
            INSERT INTO order_items
                (order_id, item_id, quantity, unit_price)
            VALUES %s;
        """

        execute_values(cursor, query, order_item_rows)

        total_order_items_inserted = total_order_items_inserted + len(order_item_rows)

        # Print progress every 1000 orders so you know the script is working.
        if order_number % 1000 == 0:
            print(f"{order_number} orders inserted so far...")

    print(f"Inserted {number_of_orders} orders.")
    print(f"Inserted {total_order_items_inserted} order items.")


# --------------------------------------------------
# Show final row counts
# --------------------------------------------------

def show_row_counts(cursor):
    """
    Prints the number of rows in each table.
    This is useful for screenshots and validation.
    """

    tables = [
        "stores",
        "ingredients",
        "menu_items",
        "customers",
        "orders",
        "order_items"
    ]

    print("\nFinal Row Counts")
    print("----------------")

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"{table}: {count}")


# --------------------------------------------------
# Main script
# --------------------------------------------------

def main():
    """
    Runs the full population process.
    """

    connection = None
    cursor = None

    try:
        print("Connecting to database...")

        connection = get_connection()
        cursor = connection.cursor()

        print("Connection successful.")

        clear_existing_data(cursor)

        store_ids = insert_stores(cursor)

        insert_ingredients(cursor)

        menu_item_prices = insert_menu_items(cursor)

        customer_ids = insert_customers(
            cursor,
            number_of_customers=1200
        )

        insert_orders_and_order_items(
            cursor=cursor,
            customer_ids=customer_ids,
            store_ids=store_ids,
            menu_item_prices=menu_item_prices,
            number_of_orders=5500
        )

        show_row_counts(cursor)

        connection.commit()

        print("\nDatabase population completed successfully.")

    except Exception as error:
        if connection is not None:
            connection.rollback()

        print("\nAn error occurred.")
        print(error)

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

        print("Database connection closed.")


if __name__ == "__main__":
    main()          