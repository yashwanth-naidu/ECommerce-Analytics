CREATE TABLE analytics.dim_customers AS
SELECT
    c.customer_id,
    c.customer_unique_id,
    c.customer_zip_code_prefix,
    c.customer_city,
    c.customer_state
FROM staging.customers c;

CREATE TABLE analytics.dim_products AS
SELECT
    p.product_id,
    COALESCE(ct.product_category_name_english, p.product_category_name, 'unknown') AS category,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    p.product_photos_qty
FROM staging.products p
LEFT JOIN staging.category_translation ct
    ON p.product_category_name = ct.product_category_name;

CREATE TABLE analytics.dim_sellers AS
SELECT
    s.seller_id,
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state
FROM staging.sellers s;

CREATE TABLE analytics.dim_dates AS
SELECT DISTINCT
    DATE(order_purchase_timestamp) AS date_key,
    EXTRACT(YEAR FROM order_purchase_timestamp) AS year,
    EXTRACT(MONTH FROM order_purchase_timestamp) AS month,
    EXTRACT(DOW FROM order_purchase_timestamp) AS day_of_week,
    EXTRACT(QUARTER FROM order_purchase_timestamp) AS quarter,
    TO_CHAR(order_purchase_timestamp, 'YYYY-MM') AS year_month
FROM staging.orders
WHERE order_purchase_timestamp IS NOT NULL;

CREATE TABLE analytics.fact_order_items AS
SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    o.customer_id,
    DATE(o.order_purchase_timestamp) AS date_key,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    oi.price,
    oi.freight_value,
    oi.price + oi.freight_value AS total_value,
    EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400.0 AS delivery_days,
    EXTRACT(EPOCH FROM (o.order_estimated_delivery_date - o.order_delivered_customer_date)) / 86400.0 AS delivery_delta_days
FROM staging.order_items oi
JOIN staging.orders o ON oi.order_id = o.order_id;

CREATE TABLE analytics.fact_reviews AS
SELECT
    r.review_id,
    r.order_id,
    r.review_score,
    r.review_creation_date,
    r.review_answer_timestamp,
    EXTRACT(EPOCH FROM (r.review_answer_timestamp - r.review_creation_date)) / 3600.0 AS response_hours
FROM staging.order_reviews r;

CREATE TABLE analytics.fact_payments AS
SELECT
    op.order_id,
    op.payment_sequential,
    op.payment_type,
    op.payment_installments,
    op.payment_value
FROM staging.order_payments op;

CREATE INDEX idx_fact_orders_date ON analytics.fact_order_items(date_key);
CREATE INDEX idx_fact_orders_customer ON analytics.fact_order_items(customer_id);
CREATE INDEX idx_fact_orders_seller ON analytics.fact_order_items(seller_id);
CREATE INDEX idx_fact_orders_product ON analytics.fact_order_items(product_id);
CREATE INDEX idx_fact_orders_status ON analytics.fact_order_items(order_status);