# 🍕 RushMore Pizzeria — Cloud Database System

> **Capstone Project | Data Engineering & Database Administration**
> Designed, deployed, and populated a production-ready PostgreSQL database on Microsoft Azure to replace a fragile JSON-based ordering system.

---

## 📌 Project Overview

RushMore Pizzeria has grown from a single outlet to a multi-location business. Their old `orders.json` file system was slow, unscalable, and unable to support concurrent users or meaningful analytics.

This project replaces that system with a **cloud-hosted relational database** (PostgreSQL on Azure), populated with **10,000+ rows of realistic synthetic data** using Python and Faker — all without exposing any real customer PII.

---

## 🗂️ Project Structure

```
rushmore-db-capstone/
│
├── README.md                        ← You are here
├── rushmore-sql-db.sql              ← Schema: all CREATE TABLE statements
├── rushmore-analytics-queries.sql   ← 5 business analytics queries
├── populate.py                      ← Python script to generate & insert fake data
├── config.yaml                      ← DB credentials (not committed — see setup)
│
└── screenshots/
    ├── azure-instance-overview.png  ← Azure PostgreSQL flexible server dashboard
    ├── azure-databases-list.png     ← rushmorecloudedb database listed
    └── pgadmin-connected.png        ← pgAdmin connected, rushmorepizza schema visible
```

---

## 🧱 Database Schema (ERD Summary)

The schema is normalized to **Third Normal Form (3NF)** across 6 tables:

```
stores ──────────────────────────────────────┐
                                             │
customers ──────────────────────────────┐   │
                                        ▼   ▼
                                      orders
                                        │
                                        ▼
menu_items ──────────────────────► order_items

ingredients  (standalone master list — not yet linked to menu_items)
```

| Table         | Description                                      | Key Columns                                      |
|---------------|--------------------------------------------------|--------------------------------------------------|
| `stores`      | Physical pizzeria locations                      | `store_id`, `city`, `address`, `phone_number`    |
| `customers`   | Registered customer accounts (PII)              | `customer_id`, `email`, `phone_number`           |
| `ingredients` | Raw ingredient master list                       | `ingredient_id`, `name`, `stock_quantity`, `unit`|
| `menu_items`  | All sellable items (pizzas, drinks, sides)       | `item_id`, `name`, `category`, `size`, `price`   |
| `orders`      | Master transaction table                         | `order_id`, `customer_id`, `store_id`, `total_amount` |
| `order_items` | Line items per order (junction table)            | `order_item_id`, `order_id`, `item_id`, `quantity`, `unit_price` |

### Key Design Decisions
- `orders.customer_id` → `ON DELETE SET NULL` (order history preserved if customer deleted)
- `orders.store_id` → `ON DELETE RESTRICT` (prevents orphaned order records)
- `order_items.order_id` → `ON DELETE CASCADE` (items removed if parent order is deleted)
- `menu_items.price` added via `ALTER TABLE` post-creation (reflects real-world schema evolution)

---

## ☁️ Cloud Deployment (Microsoft Azure)

**Service:** Azure Database for PostgreSQL — Flexible Server

| Setting              | Value                              |
|----------------------|------------------------------------|
| Server Name          | `rushmorecloudedb`                 |
| Resource Group       | `rushmoreresource`                 |
| Location             | Canada Central                     |
| PostgreSQL Version   | 18.3                               |
| Configuration        | General Purpose, D4ads v5, 4 vCores, 16 GiB |
| High Availability    | Enabled                            |
| Status               | ✅ Ready                            |
| Admin Login          | `midecloud`                        |

> **Database name:** `rushmorecloudedb`
> **Schema name:** `rushmorepizza`

### Steps Taken
1. Provisioned Azure PostgreSQL Flexible Server via Azure Portal
2. Configured firewall rules to allow client IP access
3. Connected via **pgAdmin** using the server endpoint
4. Ran `rushmore-sql-db.sql` to create all tables
5. Verified tables appeared under `rushmorepizza` schema in pgAdmin

---

## 🐍 Data Population Script (`populate.py`)

### What It Does
The script connects to the Azure PostgreSQL database and inserts synthetic but realistic data using the **Faker** library — simulating a real business without using any actual customer information.

### Libraries Used
| Library        | Purpose                                      |
|----------------|----------------------------------------------|
| `psycopg2`     | PostgreSQL connection and query execution    |
| `Faker`        | Generating realistic fake names, emails, etc.|
| `PyYAML`       | Loading DB credentials from `config.yaml`    |
| `decimal`      | Precise financial calculations               |

### Data Generated

| Table         | Volume         |
|---------------|----------------|
| Stores        | 5              |
| Ingredients   | 50             |
| Menu Items    | 25             |
| Customers     | 1,200          |
| Orders        | 5,500          |
| Order Items   | ~15,000+       |
| **Total Rows**| **~21,780+**   |

### Insertion Order (respects foreign key constraints)
```
1. stores
2. ingredients
3. menu_items
4. customers
5. orders          ← depends on stores + customers
6. order_items     ← depends on orders + menu_items
```

---

## ⚙️ How to Run the Project

### Prerequisites
- Python 3.9+
- PostgreSQL client (`psycopg2-binary`)
- A running PostgreSQL database (local or cloud)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/rushmore-db-capstone.git
cd rushmore-db-capstone
```

### 2. Install Dependencies
```bash
pip install psycopg2-binary faker pyyaml
```

### 3. Configure Your Database Credentials
Create a `config.yaml` file in the project root (this file is **not committed** to GitHub):

```yaml
database:
  host: your-server.postgres.database.azure.com
  port: 5432
  name: rushmorecloudedb
  user: your_admin_user
  password: your_password
  sslmode: require
```

### 4. Create the Schema
Connect to your database using pgAdmin or `psql` and run:
```bash
psql -h your-host -U your-user -d rushmorecloudedb -f rushmore-sql-db.sql
```

### 5. Populate with Fake Data
```bash
python populate.py
```

Expected output:
```
Connecting to database...
Connection successful.
Existing data cleared successfully.
Inserted 5 stores.
Inserted 50 ingredients.
Inserted 25 menu items.
Inserted 1200 customers.
1000 orders inserted so far...
2000 orders inserted so far...
...
Inserted 5500 orders.
Inserted ~15000 order items.

Final Row Counts
----------------
stores: 5
ingredients: 50
menu_items: 25
customers: 1200
orders: 5500
order_items: ~15000

Database population completed successfully.
Database connection closed.
```

---

## 📊 Analytics Queries (`rushmore-analytics-queries.sql`)

Five SQL queries written to answer key business questions:

### 1. Total Sales Revenue Per Store
```sql
SELECT s.store_id, s.city, COUNT(o.order_id) AS total_orders,
       SUM(o.total_amount) AS total_revenue
FROM stores s
JOIN orders o ON s.store_id = o.store_id
GROUP BY s.store_id, s.city, s.address
ORDER BY total_revenue DESC;
```

### 2. Top 10 Most Valuable Customers
```sql
SELECT c.customer_id, c.first_name, c.last_name,
       COUNT(o.order_id) AS total_orders,
       SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY total_spent DESC
LIMIT 10;
```

### 3. Most Popular Menu Item (by Quantity Sold)
```sql
SELECT mi.name, mi.category, mi.size,
       SUM(oi.quantity) AS total_quantity_sold
FROM order_items oi
JOIN menu_items mi ON oi.item_id = mi.item_id
GROUP BY mi.item_id, mi.name, mi.category, mi.size
ORDER BY total_quantity_sold DESC
LIMIT 1;
```

### 4. Average Order Value
```sql
SELECT ROUND(AVG(total_amount), 2) AS average_order_value
FROM orders;
```

### 5. Busiest Hours of the Day
```sql
SELECT EXTRACT(HOUR FROM order_timestamp) AS order_hour,
       COUNT(order_id) AS total_orders
FROM orders
GROUP BY order_hour
ORDER BY total_orders DESC;
```

---

## 🖼️ Screenshots

| Screenshot | Description |
|------------|-------------|
| `azure-instance-overview.png` | Azure portal showing `rushmorecloudedb` flexible server with status **Ready** |
| `azure-databases-list.png` | Databases panel listing `rushmorecloudedb` as a User database |
| `pgadmin-connected.png` | pgAdmin tree showing `rushmorepizza` schema connected to `rushmorecloud` server |

---      

## 🔒 Security Notes

- `config.yaml` is listed in `.gitignore` and **never committed** to the repository
- No real customer PII was used — all data is synthetic (Faker-generated)
- SSL mode is set to `require` for all Azure connections
- Database firewall restricts access to authorized IPs only

---

## 👤 Author

**Opeyemi Tayo**
Data Engineering Capstone — 2026
Azure Cloud · PostgreSQL · Python · pgAdmin
