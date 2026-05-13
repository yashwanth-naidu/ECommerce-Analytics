WITH monthly_revenue AS (
    SELECT
        d.year_month,
        SUM(f.total_value) AS revenue,
        COUNT(DISTINCT f.order_id) AS orders,
        COUNT(DISTINCT f.customer_id) AS customers
    FROM analytics.fact_order_items f
    JOIN analytics.dim_dates d ON f.date_key = d.date_key
    WHERE f.order_status = 'delivered'
    GROUP BY d.year_month
)
SELECT
    year_month,
    revenue,
    orders,
    customers,
    ROUND(revenue / NULLIF(orders, 0), 2) AS avg_order_value,
    LAG(revenue) OVER (ORDER BY year_month) AS prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY year_month))
        / NULLIF(LAG(revenue) OVER (ORDER BY year_month), 0) * 100, 2
    ) AS revenue_growth_pct,
    SUM(revenue) OVER (ORDER BY year_month) AS cumulative_revenue
FROM monthly_revenue
ORDER BY year_month;

WITH seller_metrics AS (
    SELECT
        f.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT f.order_id) AS total_orders,
        SUM(f.total_value) AS total_revenue,
        AVG(f.delivery_days) AS avg_delivery_days,
        AVG(r.review_score) AS avg_review_score
    FROM analytics.fact_order_items f
    JOIN analytics.dim_sellers s ON f.seller_id = s.seller_id
    LEFT JOIN analytics.fact_reviews r ON f.order_id = r.order_id
    WHERE f.order_status = 'delivered'
    GROUP BY f.seller_id, s.seller_city, s.seller_state
)
SELECT
    seller_id,
    seller_city,
    seller_state,
    total_orders,
    total_revenue,
    ROUND(avg_delivery_days, 1) AS avg_delivery_days,
    ROUND(avg_review_score, 2) AS avg_review_score,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
    NTILE(4) OVER (ORDER BY total_revenue DESC) AS revenue_quartile
FROM seller_metrics
ORDER BY total_revenue DESC
LIMIT 50;

WITH category_performance AS (
    SELECT
        p.category,
        COUNT(DISTINCT f.order_id) AS orders,
        SUM(f.price) AS revenue,
        AVG(f.price) AS avg_price,
        AVG(r.review_score) AS avg_review,
        AVG(f.delivery_days) AS avg_delivery_days
    FROM analytics.fact_order_items f
    JOIN analytics.dim_products p ON f.product_id = p.product_id
    LEFT JOIN analytics.fact_reviews r ON f.order_id = r.order_id
    WHERE f.order_status = 'delivered'
    GROUP BY p.category
    HAVING COUNT(DISTINCT f.order_id) >= 50
)
SELECT
    category,
    orders,
    ROUND(revenue, 2) AS revenue,
    ROUND(avg_price, 2) AS avg_price,
    ROUND(avg_review, 2) AS avg_review,
    ROUND(avg_delivery_days, 1) AS avg_delivery_days,
    ROUND(revenue * 100.0 / SUM(revenue) OVER(), 2) AS revenue_share_pct,
    ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rank
FROM category_performance
ORDER BY revenue DESC;

WITH customer_orders AS (
    SELECT
        customer_id,
        MIN(date_key) AS first_order_date,
        MAX(date_key) AS last_order_date,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(total_value) AS lifetime_value
    FROM analytics.fact_order_items
    WHERE order_status = 'delivered'
    GROUP BY customer_id
),
cohorts AS (
    SELECT
        customer_id,
        TO_CHAR(first_order_date, 'YYYY-MM') AS cohort_month,
        order_count,
        lifetime_value
    FROM customer_orders
)
SELECT
    cohort_month,
    COUNT(*) AS cohort_size,
    ROUND(AVG(lifetime_value), 2) AS avg_ltv,
    ROUND(AVG(order_count), 2) AS avg_orders,
    SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(
        SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS repeat_rate_pct
FROM cohorts
GROUP BY cohort_month
ORDER BY cohort_month;

WITH delivery_analysis AS (
    SELECT
        f.order_id,
        s.seller_state,
        c.customer_state,
        f.delivery_days,
        f.delivery_delta_days,
        CASE
            WHEN f.delivery_delta_days > 0 THEN 'early'
            WHEN f.delivery_delta_days = 0 THEN 'on_time'
            ELSE 'late'
        END AS delivery_status
    FROM analytics.fact_order_items f
    JOIN analytics.dim_sellers s ON f.seller_id = s.seller_id
    JOIN analytics.dim_customers c ON f.customer_id = c.customer_id
    WHERE f.order_status = 'delivered'
      AND f.delivery_days IS NOT NULL
)
SELECT
    seller_state,
    customer_state,
    COUNT(*) AS shipments,
    ROUND(AVG(delivery_days), 1) AS avg_delivery_days,
    ROUND(
        SUM(CASE WHEN delivery_status = 'late' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS late_delivery_pct,
    ROUND(
        SUM(CASE WHEN delivery_status = 'early' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS early_delivery_pct
FROM delivery_analysis
GROUP BY seller_state, customer_state
HAVING COUNT(*) >= 20
ORDER BY late_delivery_pct DESC;

SELECT
    payment_type,
    COUNT(*) AS transaction_count,
    SUM(payment_value) AS total_value,
    ROUND(AVG(payment_value), 2) AS avg_value,
    ROUND(AVG(payment_installments), 1) AS avg_installments,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS usage_pct
FROM analytics.fact_payments
GROUP BY payment_type
ORDER BY total_value DESC;

WITH daily_orders AS (
    SELECT
        date_key,
        COUNT(DISTINCT order_id) AS orders,
        SUM(total_value) AS revenue
    FROM analytics.fact_order_items
    WHERE order_status = 'delivered'
    GROUP BY date_key
)
SELECT
    date_key,
    orders,
    revenue,
    ROUND(AVG(orders) OVER (ORDER BY date_key ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS orders_7d_avg,
    ROUND(AVG(revenue) OVER (ORDER BY date_key ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS revenue_7d_avg,
    ROUND(AVG(revenue) OVER (ORDER BY date_key ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 2) AS revenue_30d_avg
FROM daily_orders
ORDER BY date_key;

WITH state_kpis AS (
    SELECT
        c.customer_state,
        COUNT(DISTINCT f.order_id) AS orders,
        COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
        SUM(f.total_value) AS revenue,
        AVG(r.review_score) AS avg_satisfaction,
        AVG(f.delivery_days) AS avg_delivery
    FROM analytics.fact_order_items f
    JOIN analytics.dim_customers c ON f.customer_id = c.customer_id
    LEFT JOIN analytics.fact_reviews r ON f.order_id = r.order_id
    WHERE f.order_status = 'delivered'
    GROUP BY c.customer_state
)
SELECT
    customer_state,
    orders,
    unique_customers,
    ROUND(revenue, 2) AS revenue,
    ROUND(revenue / NULLIF(unique_customers, 0), 2) AS revenue_per_customer,
    ROUND(avg_satisfaction, 2) AS avg_satisfaction,
    ROUND(avg_delivery, 1) AS avg_delivery_days,
    RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM state_kpis
ORDER BY revenue DESC;