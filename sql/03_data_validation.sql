SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM staging.customers
UNION ALL SELECT 'orders', COUNT(*) FROM staging.orders
UNION ALL SELECT 'order_items', COUNT(*) FROM staging.order_items
UNION ALL SELECT 'order_payments', COUNT(*) FROM staging.order_payments
UNION ALL SELECT 'order_reviews', COUNT(*) FROM staging.order_reviews
UNION ALL SELECT 'products', COUNT(*) FROM staging.products
UNION ALL SELECT 'sellers', COUNT(*) FROM staging.sellers
UNION ALL SELECT 'geolocation', COUNT(*) FROM staging.geolocation
UNION ALL SELECT 'category_translation', COUNT(*) FROM staging.category_translation;

SELECT
    COUNT(*) AS total_orders,
    COUNT(DISTINCT order_id) AS unique_orders,
    COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_count
FROM staging.orders;

SELECT
    COUNT(*) AS total_customers,
    COUNT(DISTINCT customer_id) AS unique_customer_ids,
    COUNT(DISTINCT customer_unique_id) AS unique_customers
FROM staging.customers;

SELECT
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
    SUM(CASE WHEN customer_city IS NULL THEN 1 ELSE 0 END) AS null_city,
    SUM(CASE WHEN customer_state IS NULL THEN 1 ELSE 0 END) AS null_state
FROM staging.customers;

SELECT
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS null_order_id,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
    SUM(CASE WHEN order_status IS NULL THEN 1 ELSE 0 END) AS null_status,
    SUM(CASE WHEN order_purchase_timestamp IS NULL THEN 1 ELSE 0 END) AS null_purchase_ts,
    SUM(CASE WHEN order_delivered_customer_date IS NULL THEN 1 ELSE 0 END) AS null_delivered_date
FROM staging.orders;

SELECT
    SUM(CASE WHEN price < 0 THEN 1 ELSE 0 END) AS negative_prices,
    SUM(CASE WHEN freight_value < 0 THEN 1 ELSE 0 END) AS negative_freight,
    SUM(CASE WHEN price IS NULL THEN 1 ELSE 0 END) AS null_prices
FROM staging.order_items;

SELECT order_status, COUNT(*) AS order_count
FROM staging.orders
GROUP BY order_status
ORDER BY order_count DESC;

SELECT
    MIN(order_purchase_timestamp) AS earliest_order,
    MAX(order_purchase_timestamp) AS latest_order,
    MAX(order_purchase_timestamp) - MIN(order_purchase_timestamp) AS date_range
FROM staging.orders;

SELECT oi.order_id
FROM staging.order_items oi
LEFT JOIN staging.orders o ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;

SELECT oi.product_id
FROM staging.order_items oi
LEFT JOIN staging.products p ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;

SELECT oi.seller_id
FROM staging.order_items oi
LEFT JOIN staging.sellers s ON oi.seller_id = s.seller_id
WHERE s.seller_id IS NULL;

SELECT
    review_score,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct
FROM staging.order_reviews
GROUP BY review_score
ORDER BY review_score;