import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="E-Commerce Analytics", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display: none;}
</style>
""", unsafe_allow_html=True)

DATA_DIR = "../data"

@st.cache_data
def load_data():
    customers = pd.read_csv(f"{DATA_DIR}/olist_customers_dataset.csv")
    orders = pd.read_csv(f"{DATA_DIR}/olist_orders_dataset.csv",
                         parse_dates=["order_purchase_timestamp", "order_delivered_customer_date",
                                      "order_estimated_delivery_date"])
    order_items = pd.read_csv(f"{DATA_DIR}/olist_order_items_dataset.csv")
    payments = pd.read_csv(f"{DATA_DIR}/olist_order_payments_dataset.csv")
    reviews = pd.read_csv(f"{DATA_DIR}/olist_order_reviews_dataset.csv")
    products = pd.read_csv(f"{DATA_DIR}/olist_products_dataset.csv")
    sellers = pd.read_csv(f"{DATA_DIR}/olist_sellers_dataset.csv")
    categories = pd.read_csv(f"{DATA_DIR}/product_category_name_translation.csv")

    products = products.merge(categories, on="product_category_name", how="left")
    products["category"] = products["product_category_name_english"].fillna("unknown")

    df = order_items.merge(orders, on="order_id") \
        .merge(customers, on="customer_id") \
        .merge(products[["product_id", "category"]], on="product_id") \
        .merge(sellers, on="seller_id")

    df = df[df["order_status"] == "delivered"].copy()
    df["total_value"] = df["price"] + df["freight_value"]
    df["delivery_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
    df["is_late"] = (df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]).astype(int)
    df["order_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)

    return df, payments, reviews

df, payments, reviews = load_data()

st.title("E-Commerce Analytics")
st.write("Analyzing 96K+ delivered orders from the Olist Brazilian e-commerce platform (2016-2018)")
st.markdown("---")

total_revenue = df["total_value"].sum()
total_orders = df["order_id"].nunique()
total_customers = df["customer_unique_id"].nunique()
avg_order_value = total_revenue / total_orders
median_delivery = df["delivery_days"].median()
late_rate = df["is_late"].mean() * 100
review_data = df.drop_duplicates("order_id").merge(reviews[["order_id", "review_score"]], on="order_id", how="left")
avg_satisfaction = review_data["review_score"].mean()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Revenue", f"R$ {total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Unique Customers", f"{total_customers:,}")
col4.metric("Avg Order Value", f"R$ {avg_order_value:,.2f}")
col5.metric("Median Delivery", f"{median_delivery:.0f} days")
col6.metric("Satisfaction", f"{avg_satisfaction:.2f} / 5")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Revenue", "Categories", "Delivery", "Customers", "Payments"])

with tab1:
    monthly = df.groupby("order_month").agg(
        revenue=("total_value", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique")
    ).reset_index()
    monthly["aov"] = monthly["revenue"] / monthly["orders"]
    monthly["growth"] = monthly["revenue"].pct_change() * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["order_month"], y=monthly["revenue"],
                              mode="lines+markers", line=dict(color="#2563eb", width=2),
                              fill="tozeroy", fillcolor="rgba(37,99,235,0.08)"))
    fig.update_layout(title="Monthly Revenue Trend", height=400,
                      xaxis_title="Month", yaxis_title="Revenue (BRL)", xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig2 = px.bar(monthly, x="order_month", y="orders", title="Monthly Orders",
                      color_discrete_sequence=["#2563eb"])
        fig2.update_layout(height=350, xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        fig3 = px.line(monthly, x="order_month", y="aov", title="Average Order Value",
                       markers=True, color_discrete_sequence=["#dc2626"])
        fig3.update_layout(height=350, xaxis_tickangle=-45)
        st.plotly_chart(fig3, use_container_width=True)

with tab2:
    cat_data = df.groupby("category").agg(
        revenue=("price", "sum"),
        orders=("order_id", "nunique"),
        avg_price=("price", "mean")
    ).sort_values("revenue", ascending=False).head(15).reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig4 = px.bar(cat_data, x="revenue", y="category", orientation="h",
                      title="Top 15 Categories by Revenue", color_discrete_sequence=["#2563eb"])
        fig4.update_layout(height=500, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig4, use_container_width=True)
    with c2:
        fig5 = px.bar(cat_data, x="orders", y="category", orientation="h",
                      title="Top 15 Categories by Orders", color_discrete_sequence=["#16a34a"])
        fig5.update_layout(height=500, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig5, use_container_width=True)

    fig6 = px.scatter(cat_data, x="avg_price", y="orders", size="revenue",
                      hover_name="category", title="Price vs Volume by Category",
                      color_discrete_sequence=["#7c3aed"])
    fig6.update_layout(height=400)
    st.plotly_chart(fig6, use_container_width=True)

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        delivery_valid = df[df["delivery_days"].between(0, 60)]
        fig7 = px.histogram(delivery_valid, x="delivery_days", nbins=40,
                            title="Delivery Time Distribution", color_discrete_sequence=["#2563eb"])
        fig7.add_vline(x=delivery_valid["delivery_days"].median(),
                       line_dash="dash", line_color="#dc2626",
                       annotation_text=f"Median: {delivery_valid['delivery_days'].median():.0f}d")
        fig7.update_layout(height=400)
        st.plotly_chart(fig7, use_container_width=True)

    with c2:
        state_late = df.groupby("seller_state").agg(
            late_rate=("is_late", "mean"), count=("order_id", "count")
        ).reset_index()
        state_late = state_late[state_late["count"] >= 100].sort_values("late_rate", ascending=False).head(15)
        state_late["late_pct"] = state_late["late_rate"] * 100
        fig8 = px.bar(state_late, x="late_pct", y="seller_state", orientation="h",
                      title="Late Delivery Rate by Seller State", color_discrete_sequence=["#dc2626"])
        fig8.update_layout(height=400, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig8, use_container_width=True)

    late_impact = review_data.copy()
    late_impact["delivery_status"] = late_impact["is_late"].map({0: "On-time", 1: "Late"})
    fig9 = px.box(late_impact.dropna(subset=["review_score"]),
                  x="delivery_status", y="review_score",
                  title="Review Score: On-time vs Late Deliveries",
                  color="delivery_status",
                  color_discrete_map={"On-time": "#16a34a", "Late": "#dc2626"})
    fig9.update_layout(height=350)
    st.plotly_chart(fig9, use_container_width=True)

with tab4:
    customer_ltv = df.groupby("customer_unique_id").agg(
        order_count=("order_id", "nunique"),
        total_spend=("total_value", "sum"),
        first_order=("order_purchase_timestamp", "min")
    ).reset_index()
    customer_ltv["cohort"] = customer_ltv["first_order"].dt.to_period("M").astype(str)

    repeat_rate = (customer_ltv["order_count"] > 1).mean() * 100
    avg_ltv = customer_ltv["total_spend"].mean()
    st.info(f"Repeat Purchase Rate: {repeat_rate:.2f}% | Average Customer LTV: R$ {avg_ltv:,.2f}")

    c1, c2 = st.columns(2)
    with c1:
        spend_bins = [0, 50, 100, 200, 500, 1000, float("inf")]
        spend_labels = ["0-50", "50-100", "100-200", "200-500", "500-1K", "1K+"]
        customer_ltv["segment"] = pd.cut(customer_ltv["total_spend"], bins=spend_bins, labels=spend_labels)
        seg_data = customer_ltv["segment"].value_counts().sort_index().reset_index()
        seg_data.columns = ["segment", "count"]
        fig10 = px.bar(seg_data, x="segment", y="count", title="Customer Spend Segments",
                       color_discrete_sequence=["#2563eb"])
        fig10.update_layout(height=350)
        st.plotly_chart(fig10, use_container_width=True)

    with c2:
        cohort_data = customer_ltv.groupby("cohort").agg(
            size=("customer_unique_id", "count"),
            avg_ltv=("total_spend", "mean")
        ).reset_index()
        fig11 = go.Figure()
        fig11.add_trace(go.Bar(x=cohort_data["cohort"], y=cohort_data["size"],
                               name="Cohort Size", marker_color="#2563eb"))
        fig11.add_trace(go.Scatter(x=cohort_data["cohort"], y=cohort_data["avg_ltv"],
                                    name="Avg LTV", yaxis="y2", mode="lines+markers",
                                    line=dict(color="#dc2626", width=2)))
        fig11.update_layout(title="Cohort Size and LTV", height=350,
                            yaxis=dict(title="Cohort Size"),
                            yaxis2=dict(title="Avg LTV (BRL)", overlaying="y", side="right"),
                            xaxis_tickangle=-45)
        st.plotly_chart(fig11, use_container_width=True)

with tab5:
    payment_data = payments.groupby("payment_type").agg(
        transactions=("payment_value", "count"),
        total_value=("payment_value", "sum"),
        avg_value=("payment_value", "mean"),
        avg_installments=("payment_installments", "mean")
    ).sort_values("total_value", ascending=False).reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig12 = px.pie(payment_data, values="total_value", names="payment_type",
                       title="Payment Method Share",
                       color_discrete_sequence=["#2563eb", "#16a34a", "#eab308", "#dc2626", "#7c3aed"])
        fig12.update_layout(height=400)
        st.plotly_chart(fig12, use_container_width=True)

    with c2:
        credit = payments[payments["payment_type"] == "credit_card"]
        inst_data = credit["payment_installments"].value_counts().sort_index().head(12).reset_index()
        inst_data.columns = ["installments", "count"]
        fig13 = px.bar(inst_data, x="installments", y="count",
                       title="Credit Card Installment Distribution",
                       color_discrete_sequence=["#2563eb"])
        fig13.update_layout(height=400)
        st.plotly_chart(fig13, use_container_width=True)

    st.dataframe(payment_data.style.format({
        "transactions": "{:,}",
        "total_value": "R$ {:,.2f}",
        "avg_value": "R$ {:,.2f}",
        "avg_installments": "{:.1f}"
    }), use_container_width=True)

st.markdown("---")
st.caption("Data source: Olist Brazilian E-Commerce Dataset (Kaggle)")