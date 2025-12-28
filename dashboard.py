import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

@st.cache_data
def load_data():
    """
    Memuat dan menggabungkan data. 
    Menggunakan st.cache_data agar tidak perlu loading ulang setiap kali filter diganti.
    """
    orders_df = pd.read_csv("data/olist_orders_dataset.csv")
    items_df = pd.read_csv("data/olist_order_items_dataset.csv")
    products_df = pd.read_csv("data/olist_products_dataset.csv")
    payments_df = pd.read_csv("data/olist_order_payments_dataset.csv")
    reviews_df = pd.read_csv("data/olist_order_reviews_dataset.csv")
    customers_df = pd.read_csv("data/olist_customers_dataset.csv")
    
    # Merging data (Sama seperti di Notebook)
    merged_df = pd.merge(orders_df, items_df, on='order_id', how='left')
    merged_df = pd.merge(merged_df, products_df, on='product_id', how='left')
    merged_df = pd.merge(merged_df, payments_df, on='order_id', how='left')
    merged_df = pd.merge(merged_df, reviews_df, on='order_id', how='left')
    merged_df = pd.merge(merged_df, customers_df, on='customer_id', how='left')
    
    # Convert datetime
    date_cols = ['order_purchase_timestamp', 'order_delivered_customer_date']
    for col in date_cols:
        merged_df[col] = pd.to_datetime(merged_df[col])
        
    # Cleaning sederhana
    clean_df = merged_df[merged_df['order_status'] == 'delivered']
    clean_df = clean_df.dropna(subset=['product_category_name'])
    
    return clean_df

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").price.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_rfm_df(df):
    # Set snapshot date ke 1 hari setelah transaksi terakhir di data filtered
    now = df['order_purchase_timestamp'].max() + pd.to_timedelta(1, unit='D')
    
    rfm_df = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (now - x.max()).days,
        'order_id': 'nunique',
        'price': 'sum'
    }).reset_index()
    
    rfm_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    return rfm_df

# --- Main Layout ---
st.set_page_config(page_title="Olist E-Commerce Dashboard", layout="wide")

# Load Data
all_df = load_data()

# Sidebar untuk Filter
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/77/Streamlit-logo-primary-colormark-darktext.png", width=150) # Logo Streamlit dummy
    st.header("Filter Data")
    
    # Rentang Waktu
    min_date = all_df["order_purchase_timestamp"].min()
    max_date = all_df["order_purchase_timestamp"].max()
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan input tanggal
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# Siapkan DataFrame untuk visualisasi
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
rfm_df = create_rfm_df(main_df)

# Header
st.title('📊 Olist E-Commerce Dashboard')
st.markdown("Dashboard ini menampilkan performa penjualan dan analisis pelanggan berdasarkan dataset Olist.")

# Key Metrics
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

with col3:
    avg_order = format_currency(daily_orders_df.revenue.mean(), "BRL", locale='es_CO')
    st.metric("Average Daily Revenue", value=avg_order)

st.divider()

# Chart 1: Daily Orders Trend
st.subheader("Tren Penjualan Harian")
fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

# Chart 2: Best & Worst Performing Product Categories
st.subheader("Performa Kategori Produk")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="price", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Top 5 Kategori (Revenue Tertinggi)", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)

sns.barplot(x="price", y="product_category_name", data=sum_order_items_df.sort_values(by="price", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Bottom 5 Kategori (Revenue Terendah)", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

st.pyplot(fig)

st.divider()

# Chart 3: RFM Analysis (Customer Segmentation)
st.subheader("Customer Segmentation (RFM Analysis)")
col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (Days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "BRL", locale='es_CO')
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(figsize=(12, 6))
sns.histplot(rfm_df['recency'], bins=30, kde=True, ax=ax, color='green')
ax.set_title('Distribusi Recency Pelanggan')
st.pyplot(fig)

# Insight Section
with st.expander("Lihat Insight Analisis"):
    st.markdown("""
    - **Tren Penjualan:** Penjualan cenderung meningkat di akhir tahun, dengan lonjakan signifikan pada periode event belanja tertentu.
    - **Produk:** Kategori *Health Beauty* dan *Bed Bath Table* adalah penyumbang revenue terbesar.
    - **Pelanggan:** Rata-rata pelanggan Olist jarang melakukan *repeat order* (Average Frequency mendekati 1), yang menunjukkan perlunya strategi retensi pelanggan yang lebih baik.
    """)

st.caption('Copyright (c) 2025 Farhan')