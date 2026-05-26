-- 1. Total sales revenue per store
SELECT
    s.store_id,
    s.city,
    s.address,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_revenue
FROM stores s
JOIN orders o 
    ON s.store_id = o.store_id
GROUP BY 
    s.store_id,
    s.city,
    s.address
ORDER BY total_revenue DESC;

-- 2. Top 10 most valuable customers by total spending
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o 
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email
ORDER BY total_spent DESC
LIMIT 10;


-- 3. Most popular menu item by quantity sold across all stores
SELECT
    mi.item_id,
    mi.name,
    mi.category,
    mi.size,
    SUM(oi.quantity) AS total_quantity_sold
FROM order_items oi
JOIN menu_items mi 
    ON oi.item_id = mi.item_id
GROUP BY
    mi.item_id,
    mi.name,
    mi.category,
    mi.size
ORDER BY total_quantity_sold DESC
LIMIT 1;

-- 4. Average order value
SELECT
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM orders;

-- 5. Busiest hours of the day for orders
SELECT
    EXTRACT(HOUR FROM order_timestamp) AS order_hour,
    COUNT(order_id) AS total_orders
FROM orders
GROUP BY order_hour
ORDER BY total_orders DESC;