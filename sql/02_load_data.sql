COPY staging.customers FROM '/path/to/data/olist_customers_dataset.csv' DELIMITER ',' CSV HEADER;

COPY staging.orders FROM '/path/to/data/olist_orders_dataset.csv' DELIMITER ',' CSV HEADER;

COPY staging.order_items FROM '/path/to/data/olist_order_items_dataset.csv' DELIMITER ',' CSV HEADER;

COPY staging.order_payments FROM '/path/to/data/olist_order_payments_dataset.csv' DELIMITER ',' CSV HEADER;

COPY staging.order_reviews FROM '/path/to/data/olist_order_reviews_dataset.csv' DELIMITER ',' CSV HEADER;

COPY staging.products FROM '/path/to/data/olist_products_dataset.csv' DELIMITER ',' CSV HEADER;

COPY staging.sellers FROM '/path/to/data/olist_sellers_dataset.csv' DELIMITER ',' CSV HEADER;

COPY staging.geolocation FROM '/path/to/data/olist_geolocation_dataset.csv' DELIMITER ',' CSV HEADER;

COPY staging.category_translation FROM '/path/to/data/product_category_name_translation.csv' DELIMITER ',' CSV HEADER;