# E-Commerce Analytics — Business Insights Report

## Executive Summary

This analysis covers 96,478 delivered orders from the Olist Brazilian e-commerce platform spanning 2016-2018, representing 93,358 unique customers and R$ 15.4M in total revenue. Key findings reveal strong revenue growth with significant operational challenges in delivery performance and customer retention.

## KPI Framework

### Revenue Metrics
- Total Revenue: R$ 15,419,773.75
- Average Order Value: R$ 159.83
- Revenue shows consistent month-over-month growth through mid-2018
- Credit card is the dominant payment method (73.9% of transactions)

### Operational Metrics
- Median delivery time: 10 days
- Late delivery rate: 7.4% of all orders
- Orders from sellers in SP state have the fastest delivery times
- Cross-state shipments to northern states show the highest delay rates

### Customer Metrics
- Repeat purchase rate: 3.00%
- Average customer lifetime value: R$ 159.83 (essentially single-purchase)
- SP, RJ, and MG account for over 60% of all customers
- Peak ordering hour: 16:00, with Monday-Wednesday being the busiest days

## Key Findings

### 1. Delivery Performance Directly Impacts Customer Satisfaction
Orders delivered late receive significantly lower review scores (avg ~2.5) compared to on-time deliveries (avg ~4.2). This 1.7-point gap represents the single largest driver of negative reviews. Reducing late deliveries by even 50% could meaningfully improve overall platform satisfaction scores.

### 2. Geographic Concentration Creates Both Opportunity and Risk
Sao Paulo state dominates across all metrics — most sellers, most customers, highest revenue, fastest delivery. This concentration means SP-to-SP transactions are the most efficient, but it also means the platform is underserving northern and northeastern states where delivery times are 2-3x longer.

### 3. Health & Beauty Leads Category Performance
Health & beauty is the top revenue category, followed by watches and bed/bath/table. High-ticket categories like computers and electronics generate strong per-order revenue but lower volume. Categories with high freight-to-price ratios (furniture, garden tools) may need pricing strategy adjustments.

### 4. Payment Installments Signal Price Sensitivity
Brazilian consumers heavily use installment payments — the average credit card transaction uses 3-4 installments. Higher-priced categories show more installments, suggesting price sensitivity. This has implications for product pricing and promotional strategies.

### 5. Customer Retention is the Biggest Growth Lever
With a repeat purchase rate of only 3.00%, nearly all revenue comes from first-time buyers. Even a modest improvement to 5-7% repeat rate would significantly reduce customer acquisition costs and increase LTV. Post-purchase engagement (delivery updates, review follow-ups, personalized recommendations) could drive this.

## Recommendations

### Short-term (0-3 months)
- Implement delivery time alerts for orders at risk of missing estimated dates
- Prioritize seller onboarding in underserved regions to reduce cross-state shipping distances
- Add installment options for categories currently limited to single payments

### Medium-term (3-6 months)
- Build a seller performance scoring system based on delivery speed, review scores, and order volume
- Launch post-purchase email sequences to drive repeat purchases
- Develop regional pricing strategies accounting for freight cost variations

### Long-term (6-12 months)
- Invest in regional fulfillment centers to reduce delivery times in northern states
- Build a customer segmentation model for targeted marketing
- Develop demand forecasting by category and region to optimize seller inventory planning

## Data Quality Notes
- Geolocation table contains duplicate zip codes with slightly different coordinates — deduplicated by taking the mean lat/lng per zip code
- Some orders have null delivery dates despite delivered status — excluded from delivery time calculations
- Product category translations are missing for ~1% of products — categorized as unknown
- Review scores show a J-shaped distribution (many 1s and 5s) typical of voluntary review systems