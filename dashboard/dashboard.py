import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def load_data():
    DATASET = "olistbr/brazilian-ecommerce"
    DATA_DIR = "./olist_data"
    os.makedirs(DATA_DIR, exist_ok=True)

    REQUIRED_FILES = [
        "olist_order_items_dataset.csv",
        "olist_order_payments_dataset.csv",
        "olist_customers_dataset.csv",
        "olist_orders_dataset.csv",
        "olist_products_dataset.csv",
        "product_category_name_translation.csv"
    ]

    for file in REQUIRED_FILES:
        file_path = os.path.join(DATA_DIR, file)
    dataframes = {file: pd.read_csv(os.path.join(DATA_DIR, file)) for file in REQUIRED_FILES}

    product_sales = dataframes["olist_order_items_dataset.csv"].merge(
        dataframes["olist_products_dataset.csv"], on="product_id"
    ).merge(
        dataframes["product_category_name_translation.csv"],
        left_on="product_category_name",
        right_on="product_category_name"
    )

    payment_analysis = dataframes["olist_orders_dataset.csv"].merge(
        dataframes["olist_order_payments_dataset.csv"], on="order_id"
    )

    customer_distribution = dataframes["olist_customers_dataset.csv"].merge(
        dataframes["olist_orders_dataset.csv"], on="customer_id"
    )
    customer_distribution["order_day"] = pd.to_datetime(customer_distribution["order_purchase_timestamp"]).dt.day_name()

    return product_sales, payment_analysis, customer_distribution

product_sales, payment_analysis, customer_distribution = load_data()

# Streamlit App
st.title("E-Commerce Data Analysis Dashboard")

# Top Selling Products
st.subheader("Top 10 Best Selling Product Categories")
if not product_sales.empty:
    top_products = product_sales.groupby("product_category_name_english")["order_id"].count().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_products.values, y=top_products.index, palette="viridis", ax=ax)
    ax.set_xlabel("Number of Orders")
    ax.set_ylabel("Product Category")
    ax.set_title("Top 10 Product Categories by Orders")
    st.pyplot(fig)
else:
    st.warning("No data available for product sales.")

# Payment Methods
st.subheader("Most Used Payment Methods")
if not payment_analysis.empty:
    payment_counts = payment_analysis["payment_type"].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=payment_counts.values, y=payment_counts.index, palette="magma", ax=ax)
    ax.set_xlabel("Number of Transactions")
    ax.set_ylabel("Payment Method")
    ax.set_title("Top Payment Methods")
    st.pyplot(fig)
else:
    st.warning("No data available for payment analysis.")

# Customer Distribution
st.subheader("Customer Distribution by Province")
if not customer_distribution.empty:
    customer_counts = customer_distribution["customer_state"].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=customer_counts.values, y=customer_counts.index, palette="coolwarm", ax=ax)
    ax.set_xlabel("Number of Customers")
    ax.set_ylabel("Province")
    ax.set_title("Customer Distribution by Province")
    st.pyplot(fig)
else:
    st.warning("No data available for customer distribution.")

# Shopping Frequency by Day
st.subheader("Most Popular Shopping Days")
if "order_day" in customer_distribution.columns:
    order_days = customer_distribution["order_day"].value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=order_days.index, y=order_days.values, palette="Blues", ax=ax)
    ax.set_xlabel("Day of the Week")
    ax.set_ylabel("Number of Orders")
    ax.set_title("Shopping Frequency by Day")
    st.pyplot(fig)
else:
    st.warning("No data available for shopping frequency.")
