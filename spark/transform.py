from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("OlistECommerceAnalytics") \
    .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
    .getOrCreate()

DATA_DIR = "../data"

customers = spark.read.csv(f"{DATA_DIR}/olist_customers_dataset.csv", header=True, inferSchema=True)
orders = spark.read.csv(f"{DATA_DIR}/olist_orders_dataset.csv", header=True, inferSchema=True)
order_items = spark.read.csv(f"{DATA_DIR}/olist_order_items_dataset.csv", header=True, inferSchema=True)
payments = spark.read.csv(f"{DATA_DIR}/olist_order_payments_dataset.csv", header=True, inferSchema=True)
reviews = spark.read.csv(f"{DATA_DIR}/olist_order_reviews_dataset.csv", header=True, inferSchema=True)
products = spark.read.csv(f"{DATA_DIR}/olist_products_dataset.csv", header=True, inferSchema=True)
sellers = spark.read.csv(f"{DATA_DIR}/olist_sellers_dataset.csv", header=True, inferSchema=True)
categories = spark.read.csv(f"{DATA_DIR}/product_category_name_translation.csv", header=True, inferSchema=True)

print("=== Record Counts ===")
for name, df in [("customers", customers), ("orders", orders), ("order_items", order_items),
                  ("payments", payments), ("reviews", reviews), ("products", products),
                  ("sellers", sellers), ("categories", categories)]:
    print(f"{name}: {df.count()}")

orders_clean = orders.filter(F.col("order_status") == "delivered") \
    .dropDuplicates(["order_id"]) \
    .withColumn("order_purchase_timestamp", F.to_timestamp("order_purchase_timestamp")) \
    .withColumn("order_delivered_customer_date", F.to_timestamp("order_delivered_customer_date")) \
    .withColumn("order_estimated_delivery_date", F.to_timestamp("order_estimated_delivery_date"))

order_items_clean = order_items \
    .filter((F.col("price") > 0) & (F.col("freight_value") >= 0)) \
    .withColumn("total_value", F.col("price") + F.col("freight_value"))

products_enriched = products \
    .join(categories, "product_category_name", "left") \
    .withColumn("category", F.coalesce(F.col("product_category_name_english"), F.lit("unknown"))) \
    .withColumn("volume_cm3",
                F.col("product_length_cm") * F.col("product_height_cm") * F.col("product_width_cm")) \
    .drop("product_category_name", "product_category_name_english")

enriched_orders = order_items_clean \
    .join(orders_clean, "order_id") \
    .join(customers, "customer_id") \
    .join(products_enriched, "product_id") \
    .join(sellers, "seller_id") \
    .withColumn("delivery_days",
                F.datediff(F.col("order_delivered_customer_date"), F.col("order_purchase_timestamp"))) \
    .withColumn("estimated_days",
                F.datediff(F.col("order_estimated_delivery_date"), F.col("order_purchase_timestamp"))) \
    .withColumn("delivery_delta", F.col("estimated_days") - F.col("delivery_days")) \
    .withColumn("is_late", F.when(F.col("delivery_delta") < 0, 1).otherwise(0)) \
    .withColumn("order_month", F.date_format(F.col("order_purchase_timestamp"), "yyyy-MM"))

monthly = enriched_orders.groupBy("order_month").agg(
    F.sum("total_value").alias("revenue"),
    F.countDistinct("order_id").alias("orders"),
    F.countDistinct("customer_id").alias("customers"),
    F.avg("delivery_days").alias("avg_delivery_days"),
    F.avg("is_late").alias("late_delivery_rate")
)

month_window = Window.orderBy("order_month")
monthly_kpis = monthly \
    .withColumn("avg_order_value", F.round(F.col("revenue") / F.col("orders"), 2)) \
    .withColumn("prev_revenue", F.lag("revenue").over(month_window)) \
    .withColumn("revenue_growth_pct",
                F.round((F.col("revenue") - F.col("prev_revenue")) / F.col("prev_revenue") * 100, 2)) \
    .withColumn("cumulative_revenue", F.sum("revenue").over(month_window.rowsBetween(Window.unboundedPreceding, 0))) \
    .withColumn("avg_delivery_days", F.round("avg_delivery_days", 1)) \
    .withColumn("late_delivery_rate", F.round(F.col("late_delivery_rate") * 100, 2))

print("\n=== Monthly KPIs ===")
monthly_kpis.orderBy("order_month").show(30, truncate=False)

seller_window = Window.orderBy(F.desc("total_revenue"))
seller_performance = enriched_orders.groupBy("seller_id", "seller_city", "seller_state").agg(
    F.countDistinct("order_id").alias("total_orders"),
    F.sum("total_value").alias("total_revenue"),
    F.avg("delivery_days").alias("avg_delivery_days")
).withColumn("revenue_rank", F.rank().over(seller_window)) \
 .withColumn("revenue_quartile", F.ntile(4).over(seller_window))

print("\n=== Top 20 Sellers ===")
seller_performance.orderBy("revenue_rank").show(20, truncate=False)

category_window = Window.orderBy(F.desc("revenue"))
category_analysis = enriched_orders.groupBy("category").agg(
    F.countDistinct("order_id").alias("orders"),
    F.sum("price").alias("revenue"),
    F.avg("price").alias("avg_price"),
    F.avg("delivery_days").alias("avg_delivery")
).filter(F.col("orders") >= 50) \
 .withColumn("rank", F.row_number().over(category_window)) \
 .withColumn("revenue_share_pct",
             F.round(F.col("revenue") / F.sum("revenue").over(Window.partitionBy()) * 100, 2))

print("\n=== Category Performance ===")
category_analysis.orderBy("rank").show(30, truncate=False)

customer_agg = enriched_orders.groupBy("customer_unique_id").agg(
    F.min("order_purchase_timestamp").alias("first_order"),
    F.max("order_purchase_timestamp").alias("last_order"),
    F.countDistinct("order_id").alias("order_count"),
    F.sum("total_value").alias("lifetime_value")
).withColumn("cohort_month", F.date_format("first_order", "yyyy-MM"))

cohort_analysis = customer_agg.groupBy("cohort_month").agg(
    F.count("*").alias("cohort_size"),
    F.round(F.avg("lifetime_value"), 2).alias("avg_ltv"),
    F.round(F.avg("order_count"), 2).alias("avg_orders"),
    F.sum(F.when(F.col("order_count") > 1, 1).otherwise(0)).alias("repeat_customers")
).withColumn("repeat_rate_pct",
             F.round(F.col("repeat_customers") / F.col("cohort_size") * 100, 2))

print("\n=== Cohort Analysis ===")
cohort_analysis.orderBy("cohort_month").show(30, truncate=False)

state_delivery = enriched_orders.groupBy("seller_state", "customer_state").agg(
    F.count("*").alias("shipments"),
    F.round(F.avg("delivery_days"), 1).alias("avg_delivery_days"),
    F.round(F.avg("is_late") * 100, 2).alias("late_pct")
).filter(F.col("shipments") >= 20)

print("\n=== Delivery Performance by Route ===")
state_delivery.orderBy(F.desc("late_pct")).show(30, truncate=False)

OUTPUT_DIR = "../data/processed"
monthly_kpis.coalesce(1).write.mode("overwrite").csv(f"{OUTPUT_DIR}/monthly_kpis", header=True)
seller_performance.coalesce(1).write.mode("overwrite").csv(f"{OUTPUT_DIR}/seller_performance", header=True)
category_analysis.coalesce(1).write.mode("overwrite").csv(f"{OUTPUT_DIR}/category_analysis", header=True)
cohort_analysis.coalesce(1).write.mode("overwrite").csv(f"{OUTPUT_DIR}/cohort_analysis", header=True)
state_delivery.coalesce(1).write.mode("overwrite").csv(f"{OUTPUT_DIR}/delivery_routes", header=True)

print("\n=== Processing Complete ===")
print(f"Processed {enriched_orders.count()} order items")
print(f"Output saved to {OUTPUT_DIR}")

spark.stop()