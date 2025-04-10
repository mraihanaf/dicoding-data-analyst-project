import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load datasets with caching
@st.cache_data
def load_data():
    order_items = pd.read_csv('../olist_data/olist_order_items_dataset.csv')
    order_payments = pd.read_csv('../olist_data/olist_order_payments_dataset.csv')
    customers = pd.read_csv('../olist_data/olist_customers_dataset.csv')
    orders = pd.read_csv('../olist_data/olist_orders_dataset.csv')
    products = pd.read_csv('../olist_data/olist_products_dataset.csv')
    category_translation = pd.read_csv('../olist_data/product_category_name_translation.csv')
    return order_items, order_payments, customers, orders, products, category_translation

# Load data
order_items, order_payments, customers, orders, products, category_translation = load_data()

# Convert timestamp to datetime
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])

# Sidebar Filters
st.sidebar.header('Filters')

# Date range filter
min_date = orders['order_purchase_timestamp'].min().date()
max_date = orders['order_purchase_timestamp'].max().date()
start_date = st.sidebar.date_input('Start Date', min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input('End Date', max_date, min_value=min_date, max_value=max_date)

# Product category filter
all_categories = category_translation['product_category_name_english'].dropna().unique().tolist()
selected_categories = st.sidebar.multiselect('Product Categories', all_categories, default=all_categories)

# Province filter
all_provinces = customers['customer_state'].dropna().unique().tolist()
selected_provinces = st.sidebar.multiselect('Provinces', all_provinces, default=all_provinces)

# Filter orders by date range
filtered_orders = orders[(orders['order_purchase_timestamp'].dt.date >= start_date) & 
                         (orders['order_purchase_timestamp'].dt.date <= end_date)]

# Filter customers by province and merge with orders
filtered_customers = customers[customers['customer_state'].isin(selected_provinces)]
filtered_orders = filtered_orders.merge(filtered_customers[['customer_id']], on='customer_id')

# Prepare product sales data
product_sales = order_items.merge(filtered_orders[['order_id']], on='order_id')
product_sales = product_sales.merge(products, on='product_id')
product_sales = product_sales.merge(category_translation, on='product_category_name')
product_sales = product_sales[product_sales['product_category_name_english'].isin(selected_categories)]

product_sales_count = (product_sales.groupby('product_category_name_english')['order_id']
                       .count().reset_index()
                       .rename(columns={'product_category_name_english': 'category', 'order_id': 'transaction_count'})
                       .sort_values('transaction_count', ascending=False))

# Prepare payment frequency data
filtered_payments = order_payments.merge(filtered_orders[['order_id']], on='order_id')
payment_freq = filtered_payments['payment_type'].value_counts().reset_index()
payment_freq.columns = ['payment_type', 'frequency']

# Prepare customer distribution data
customer_by_province = (filtered_customers.groupby('customer_state')['customer_unique_id']
                        .nunique().reset_index()
                        .rename(columns={'customer_state': 'province', 'customer_unique_id': 'unique_customers'})
                        .sort_values('unique_customers', ascending=False))

# Prepare orders by day of the week data
filtered_orders['order_day'] = filtered_orders['order_purchase_timestamp'].dt.day_name()
orders_by_day = (filtered_orders.groupby('order_day')['order_id']
                 .count().reset_index()
                 .rename(columns={'order_day': 'day', 'order_id': 'order_count'}))
order_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
orders_by_day['day'] = pd.Categorical(orders_by_day['day'], categories=order_days, ordered=True)
orders_by_day = orders_by_day.sort_values('day')

# Dashboard Layout
st.title('E-Commerce Data Analysis Dashboard')

# Top 10 Product Categories
st.subheader('Top 10 Categories by Transaction Count')
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y=product_sales_count['category'].head(10), x=product_sales_count['transaction_count'].head(10), palette='viridis', ax=ax)
ax.set_title('Top 10 Categories by Transaction Count')
ax.set_xlabel('Transaction Count')
ax.set_ylabel('Category')
plt.tight_layout()
st.pyplot(fig)

# Bottom 10 Product Categories
st.subheader('Bottom 10 Categories by Transaction Count')
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y=product_sales_count['category'].tail(10), x=product_sales_count['transaction_count'].tail(10), palette='viridis', ax=ax)
ax.set_title('Bottom 10 Categories by Transaction Count')
ax.set_xlabel('Transaction Count')
ax.set_ylabel('Category')
plt.tight_layout()
st.pyplot(fig)

# Payment Method Frequency
st.subheader('Top 5 Payment Methods by Number of Transactions')
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(y=payment_freq['payment_type'].head(5), x=payment_freq['frequency'].head(5), palette='viridis', ax=ax)
ax.set_title('Top 5 Payment Methods by Number of Transactions')
ax.set_xlabel('Number of Transactions')
ax.set_ylabel('Payment Method')
plt.tight_layout()
st.pyplot(fig)

# Orders by Day
st.subheader('Jumlah Pesanan Berdasarkan Hari')
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=orders_by_day['day'], y=orders_by_day['order_count'], palette='Blues_r', ax=ax)
ax.set_title('Jumlah Pesanan Berdasarkan Hari')
ax.set_xlabel('Hari')
ax.set_ylabel('Jumlah Pesanan')
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

# Customer Distribution
st.subheader('Distribusi Pelanggan Berdasarkan Provinsi')
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(y=customer_by_province['province'], x=customer_by_province['unique_customers'], palette='magma', ax=ax)
ax.set_title('Distribusi Pelanggan Berdasarkan Provinsi')
ax.set_xlabel('Jumlah Pelanggan Unik')
ax.set_ylabel('Provinsi')
plt.tight_layout()
st.pyplot(fig)

# Raw data option
if st.checkbox('Show Raw Data'):
    st.write('Product Sales:', product_sales_count)
    st.write('Payment Frequency:', payment_freq)
    st.write('Customer Distribution:', customer_by_province)
    st.write('Orders by Day:', orders_by_day)

st.write('---')
st.caption('Built with Streamlit | Data from Olist Brazilian E-Commerce')