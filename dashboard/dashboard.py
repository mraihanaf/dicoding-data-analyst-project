import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load datasets with caching
@st.cache_data
def load_data():
    order_items = pd.read_csv('./olist_data/olist_order_items_dataset.csv')
    order_payments = pd.read_csv('./olist_data/olist_order_payments_dataset.csv')
    customers = pd.read_csv('./olist_data/olist_customers_dataset.csv')
    orders = pd.read_csv('./olist_data/olist_orders_dataset.csv')
    products = pd.read_csv('./olist_data/olist_products_dataset.csv')
    category_translation = pd.read_csv('./olist_data/product_category_name_translation.csv')
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
all_categories = category_translation['product_category_name_english'].unique().tolist()
selected_categories = st.sidebar.multiselect('Product Categories', all_categories, default=all_categories)

# Province filter
all_provinces = customers['customer_state'].unique().tolist()
selected_provinces = st.sidebar.multiselect('Provinces', all_provinces, default=all_provinces)

# Data Filtering
# Filter orders by date range
filtered_orders = orders[(orders['order_purchase_timestamp'].dt.date >= start_date) & 
                         (orders['order_purchase_timestamp'].dt.date <= end_date)]

# Filter customers by province and merge with orders
filtered_customers = customers[customers['customer_state'].isin(selected_provinces)]
filtered_orders = filtered_orders.merge(filtered_customers[['customer_id']], on='customer_id')

# Data Preparation for Visualizations
# Product sales by category
product_sales = (order_items.merge(filtered_orders[['order_id']], on='order_id')
                            .merge(products, on='product_id')
                            .merge(category_translation, on='product_category_name'))
product_sales = product_sales[product_sales['product_category_name_english'].isin(selected_categories)]
product_sales_count = (product_sales.groupby('product_category_name_english')['order_id']
                          .count().reset_index()
                          .rename(columns={'product_category_name_english': 'category', 'order_id': 'transaction_count'})
                          .sort_values('transaction_count', ascending=False))

# Payment method frequency
filtered_payments = order_payments.merge(filtered_orders[['order_id']], on='order_id')
payment_freq = filtered_payments['payment_type'].value_counts().reset_index()
payment_freq.columns = ['payment_type', 'frequency']

# Customer distribution by province
customer_by_province = (filtered_customers.groupby('customer_state')['customer_unique_id']
                         .nunique().reset_index()
                         .rename(columns={'customer_state': 'province', 'customer_unique_id': 'unique_customers'})
                         .sort_values('unique_customers', ascending=False))

# Orders by day of the week
filtered_orders['order_day'] = filtered_orders['order_purchase_timestamp'].dt.day_name()
orders_by_day = (filtered_orders.groupby('order_day')['order_id']
                   .count().reset_index()
                   .rename(columns={'order_day': 'day', 'order_id': 'order_count'}))
order_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
orders_by_day['day'] = pd.Categorical(orders_by_day['day'], categories=order_days, ordered=True)
orders_by_day = orders_by_day.sort_values('day')

# Dashboard Layout
st.title('E-Commerce Data Analysis Dashboard')
st.write('This dashboard provides insights into product sales, payment methods, customer distribution, and shopping patterns.')

# Top and bottom product categories
st.subheader('Top and Bottom Product Categories by Transaction Count')
st.write('Explore the highest and lowest performing product categories based on transaction volume.')
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='transaction_count', y='category', data=product_sales_count.head(5), palette='viridis', ax=ax)
ax.set_title('Top 5 Product Categories')
ax.set_xlabel('Transaction Count')
ax.set_ylabel('Category')
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='transaction_count', y='category', data=product_sales_count.tail(5), palette='viridis', ax=ax)
ax.set_title('Bottom 5 Product Categories')
ax.set_xlabel('Transaction Count')
ax.set_ylabel('Category')
st.pyplot(fig)

# Payment method frequency
st.subheader('Payment Method Frequency')
st.write('See the most commonly used payment methods.')
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x='frequency', y='payment_type', data=payment_freq, palette='Blues_r', ax=ax)
ax.set_title('Most Used Payment Methods')
ax.set_xlabel('Frequency')
ax.set_ylabel('Payment Type')
st.pyplot(fig)

# Customer distribution by province
st.subheader('Customer Distribution by Province')
st.write('View the top provinces by unique customer count.')
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='unique_customers', y='province', data=customer_by_province.head(5), palette='Greens_r', ax=ax)
ax.set_title('Top 5 Provinces by Unique Customers')
ax.set_xlabel('Unique Customers')
ax.set_ylabel('Province')
st.pyplot(fig)

# Orders by day of the week
st.subheader('Order Count by Day of the Week')
st.write('Analyze purchasing patterns across the week.')
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='day', y='order_count', data=orders_by_day, palette='Oranges_r', ax=ax)
ax.set_title('Order Count by Day')
ax.set_xlabel('Day')
ax.set_ylabel('Order Count')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
st.pyplot(fig)

# Optional Data Tables
if st.checkbox('Show Raw Data'):
    st.subheader('Product Sales Data')
    st.write(product_sales_count)
    st.subheader('Payment Frequency Data')
    st.write(payment_freq)
    st.subheader('Customers by Province Data')
    st.write(customer_by_province)
    st.subheader('Orders by Day Data')
    st.write(orders_by_day)

# Footer
st.write('---')
st.write('Built with Streamlit by Raihan | Data Source: Olist Brazilian E-Commerce Dataset')