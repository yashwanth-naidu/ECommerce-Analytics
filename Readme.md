# E-Commerce Analytics

End-to-end data analytics project built on the Olist Brazilian E-Commerce dataset (100K+ orders), covering the complete workflow from raw data ingestion through analytical modeling, SQL insights, PySpark transformations, exploratory data analysis, and interactive dashboards.

## Business Context

Olist is a Brazilian e-commerce marketplace connecting sellers and customers across multiple product categories. This project analyzes transactional performance, delivery operations, customer behavior, and seller effectiveness to derive actionable business insights.

## Tech Stack

- **SQL (PostgreSQL):** Schema design, data modeling (star schema), data validation, advanced analytical queries (window functions, CTEs, cohort analysis)
- **Python (Pandas):** Exploratory data analysis, data profiling, trend detection, correlation analysis, visualization (Matplotlib, Seaborn)
- **PySpark:** Large-scale data transformation, aggregation pipelines, window functions, KPI computation
- **Streamlit + Plotly:** Interactive KPI dashboard with revenue tracking, category performance, delivery analytics, customer segmentation, payment analysis
- **PostgreSQL:** Staging schema, analytical star schema with fact and dimension tables, indexed for query performance

## Dataset

Source: [Olist Brazilian E-Commerce Dataset (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

9 tables covering:
- Customers (99K+ unique customers across 27 states)
- Orders (100K+ orders, 2016-2018)
- Order Items (item-level transactions with pricing and freight)
- Payments (payment method, installments, values)
- Reviews (1-5 star ratings with text)
- Products (73 categories with physical attributes)
- Sellers (3K+ sellers across Brazil)
- Geolocation (zip code coordinates)
- Category Translation (Portuguese to English)

## Project Structure

```
├── sql/
│   ├── 01_create_tables.sql        # Staging schema DDL
│   ├── 02_load_data.sql            # CSV data ingestion
│   ├── 03_data_validation.sql      # Quality checks and integrity tests
│   ├── 04_star_schema.sql          # Analytical model (fact + dimension tables)
│   └── 05_analytical_queries.sql   # Business KPIs, window functions, cohort analysis
├── spark/
│   └── transform.py                # PySpark ETL and aggregation pipeline
├── notebooks/
│   └── EDA.ipynb                   # Pandas EDA with visualizations
├── dashboard/
│   ├── app.py                      # Streamlit interactive dashboard
│   └── requirements.txt
├── reports/
│   └── business_insights.md        # Key findings and recommendations
├── data/                           # Raw CSVs (not tracked in git)
└── .gitignore
```

## Key Analyses

### SQL Analytics
- Monthly revenue trends with MoM growth (LAG, window functions)
- Seller performance ranking by revenue quartile (NTILE, RANK)
- Category performance with revenue share (SUM OVER)
- Customer cohort analysis with repeat purchase rates (CTEs)
- Delivery route performance, late delivery rates by seller-customer state pairs
- Payment method breakdown with installment patterns
- 7-day and 30-day moving averages for revenue and order volume
- State-level KPI dashboard (revenue per customer, satisfaction, delivery speed)

### PySpark Pipeline
- Reads and joins 9 raw CSV files
- Cleans and transforms 100K+ orders with derived metrics (delivery days, late flags, total value)
- Computes monthly KPIs with window functions (cumulative revenue, growth rates)
- Seller performance scoring with quartile ranking
- Category analysis with revenue share computation
- Cohort-based customer lifetime value analysis
- Outputs processed datasets to CSV for downstream consumption

### Exploratory Data Analysis (Pandas)
- Revenue and order volume trend analysis
- Category performance profiling (revenue vs volume vs price)
- Delivery time distribution and late delivery impact on reviews
- Customer segmentation by spend
- Cohort analysis with LTV tracking
- Payment behavior patterns (installment distribution)
- Geographic analysis (state-level revenue and delivery performance)
- Temporal patterns (hourly and day-of-week ordering behavior)
- Feature correlation matrix

### Interactive Dashboard (Streamlit)
- 6 KPI cards (revenue, orders, customers, AOV, delivery time, satisfaction)
- 5 tabs: Revenue, Categories, Delivery, Customers, Payments
- Revenue trend with growth visualization
- Category drill-down (revenue and volume)
- Delivery performance heatmap by state
- Customer cohort and spend segmentation
- Payment method distribution and installment analysis

## Key Findings

- Revenue grew consistently MoM through mid-2018
- Late deliveries reduce review scores by ~1.7 points (4.2 vs 2.5 avg)
- Repeat purchase rate is below 3%, biggest growth opportunity
- SP state accounts for 40%+ of orders with fastest delivery times
- Credit cards dominate at 74% of transactions, averaging 3-4 installments
- Cross-state shipments to northern regions show 2-3x longer delivery times

## Setup

### PostgreSQL
```bash
psql -U postgres -f sql/01_create_tables.sql
psql -U postgres -f sql/02_load_data.sql
psql -U postgres -f sql/03_data_validation.sql
psql -U postgres -f sql/04_star_schema.sql
psql -U postgres -f sql/05_analytical_queries.sql
```

### PySpark
```bash
cd spark
spark-submit transform.py
```

### EDA Notebook
```bash
cd notebooks
jupyter notebook EDA.ipynb
```

### Streamlit Dashboard
```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```