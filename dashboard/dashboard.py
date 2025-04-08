import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from wordcloud import WordCloud
from babel.numbers import format_currency
sns.set(style='dark')

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name")['order_id'].nunique().sort_values(ascending=False).reset_index()
    return sum_order_items_df


def create_sum_payment_value_items(df):
    sum_payment_value_items_df = df.groupby('product_category_name')['payment_value'].sum().sort_values(ascending=False).reset_index()
    return sum_payment_value_items_df

# def create_rfm_df(df):
#     df = df.copy()  # Membuat salinan DataFrame untuk menghindari modifikasi global
#     customer_id_mapping = {customer_id: i +1 for i, customer_id in enumerate(df['customer_id'].unique())}
#     df['id'] = df['customer_id'].map(customer_id_mapping)

#     rfm_df = df.groupby(by='id', as_index=False).agg({
#         "order_approved_at": "max",
#         "order_id": "nunique",
#         "payment_value": "sum"
#     })

#     rfm_df.columns = ['customer_id', 'max_order_timestamp', 'frequency', 'monetary']
#     rfm_df['max_order_timestamp'] = pd.to_datetime(rfm_df['max_order_timestamp'])
#     recent_date = pd.to_datetime(df['order_approved_at']).max()
#     rfm_df['recency'] = rfm_df['max_order_timestamp'].apply(lambda x: (recent_date - x).days)
    
#     return rfm_df

def create_wordcloud(df):
    # Menggabungkan semua komentar review dari kolom 'review_comment_message'
    text = ' '.join(df['review_comment_message'].dropna())

    # Membuat objek WordCloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    return wordcloud

def create_customer_state(df):
    customer_state_df = df.groupby('customer_state').agg(
        total_payment_value=('payment_value', 'sum'),  # Total pembayaran per state
        total_orders=('order_id', 'count'),  # Jumlah pesanan per state
        total_customers=('customer_unique_id', 'nunique'),  # Jumlah pelanggan unik per state
        average_payment_value=('payment_value', 'mean'),  # Rata-rata pembayaran per order
    ).sort_values(by='total_payment_value', ascending=False).reset_index()

    return customer_state_df

def create_customer_city(df):
    customer_city_df = df.groupby('customer_city').agg(
        total_payment_value=('payment_value', 'sum'),  # Total pembayaran per state
        total_orders=('order_id', 'count'),  # Jumlah pesanan per state
        total_customers=('customer_unique_id', 'nunique'),  # Jumlah pelanggan unik per state
        average_payment_value=('payment_value', 'mean'),  # Rata-rata pembayaran per order
    ).sort_values(by='total_payment_value', ascending=False).reset_index()

    return customer_city_df

def create_time_series_data(df):
    df = df.set_index("order_approved_at")  
    df = df.sort_index()
    
    orders_per_day = df['order_id'].resample('D').nunique()
    sales_per_day = df['payment_value'].resample('D').sum()
    
    order_status_per_day = df.groupby([pd.Grouper(freq='D'), 'order_status']).size().unstack().fillna(0)
    
    return orders_per_day, sales_per_day, order_status_per_day

file_url = "https://raw.githubusercontent.com/lovdianchel/customer-analysis-dicoding/refs/heads/main/dashboard/main_data.csv"
all_df = pd.read_csv(file_url)

datetime_columns = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column], format='mixed')

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()


with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                (all_df["order_approved_at"] <= str(end_date))]

sum_order_items_df = create_sum_order_items_df(main_df)
sum_payment_value_items_df = create_sum_payment_value_items(main_df)
wordcloud = create_wordcloud(main_df)
customer_state_df = create_customer_state(main_df)
customer_city_df = create_customer_city(main_df)
# rfm_df = create_rfm_df(all_df)
orders_per_day, sales_per_day, order_status_per_day = create_time_series_data(main_df)

st.header('Final Project Analysis Data Python :sparkles:')

# st.subheader("Data Overview")
# st.write(all_df)


# st.subheader("Best Customer Based on RFM Parameters")

# st.write(all_df.isna().sum())

# col1, col2, col3 = st.columns(3)

# with col1:
#     avg_recency = round(rfm_df.recency.mean(), 1)
#     st.metric("Average Recency (days)", value=avg_recency)

# with col2:
#     avg_frequency = round(rfm_df.frequency.mean(), 2)
#     st.metric("Average Frequency", value=avg_frequency)

# with col3:
#     avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
#     st.metric("Average Monetary", value=avg_frequency)

# fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
# colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

# sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
# ax[0].set_ylabel(None)
# ax[0].set_xlabel("customer_id", fontsize=30)
# ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
# ax[0].tick_params(axis='y', labelsize=30)
# ax[0].tick_params(axis='x', labelsize=35)

# sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
# ax[1].set_ylabel(None)
# ax[1].set_xlabel("customer_id", fontsize=30)
# ax[1].set_title("By Frequency", loc="center", fontsize=50)
# ax[1].tick_params(axis='y', labelsize=30)
# ax[1].tick_params(axis='x', labelsize=35)

# sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
# ax[2].set_ylabel(None)
# ax[2].set_xlabel("customer_id", fontsize=30)
# ax[2].set_title("By Monetary", loc="center", fontsize=50)
# ax[2].tick_params(axis='y', labelsize=30)
# ax[2].tick_params(axis='x', labelsize=35)

# st.pyplot(fig)

# Pertanyaan 1
st.subheader("Produk yang Paling Sering Terjual")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(y="order_id", x="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel("Jumlah Order")
ax[0].set_xlabel("Kategori Produk", fontsize=15)
ax[0].set_title("Best Performing Product", loc="center", fontsize=20)
ax[0].tick_params(axis='y', labelsize=15)
ax[0].tick_params(axis='x', labelsize=15)

sns.barplot(y="order_id", x="product_category_name", data=sum_order_items_df.sort_values(by="order_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel("Jumlah Order")
ax[1].set_xlabel("Kateogri Produk", fontsize=15)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=20)
ax[1].tick_params(axis='y', labelsize=15)
ax[1].tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Pertanyaan 2
# st.subheader("Produk Terjual Berdasarkan Total Nilai Transaksi")

# fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

# colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# sns.barplot(y="payment_value", x="product_category_name", data=sum_payment_value_items_df.head(5), palette=colors, ax=ax[0])
# ax[0].set_ylabel("Nilai Transaksi")
# ax[0].set_xlabel("Kategori Produk", fontsize=15)
# ax[0].set_title("Best Performing Product", loc="center", fontsize=20)
# ax[0].tick_params(axis='y', labelsize=15)
# ax[0].tick_params(axis='x', labelsize=15)

# sns.barplot(y="payment_value", x="product_category_name", data=sum_payment_value_items_df.sort_values(by="payment_value", ascending=True).head(5), palette=colors, ax=ax[1])
# ax[1].set_ylabel("Nilai Transaksi")
# ax[1].set_xlabel("Kategori Produk", fontsize=15)
# ax[1].invert_xaxis()
# ax[1].yaxis.set_label_position("right")
# ax[1].yaxis.tick_right()
# ax[1].set_title("Worst Performing Product", loc="center", fontsize=20)
# ax[1].tick_params(axis='y', labelsize=15)
# ax[1].tick_params(axis='x', labelsize=15)

# st.pyplot(fig)

# Pertanyaan 3

st.subheader("Kata-Kata yang Sering Muncul dari Review Produk")
fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")

st.pyplot(fig)

# Pertanyaan 4

st.subheader("Persebaran Lokasi Customer")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
colors2 = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"]
colors3 = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]


sns.barplot(y="total_customers", x="customer_state", data=customer_state_df.head(5), palette=colors, ax=axes[0,0])
axes[0, 0].set_ylabel("Jumlah customer")
axes[0, 0].set_xlabel("State")
axes[0, 0].set_title("State dengan customer paling banyak", loc="center", fontsize=15)
axes[0, 0].tick_params(axis='x', labelsize=15)

sns.barplot(y="total_customers", x="customer_state", data=customer_state_df.sort_values(by="total_customers", ascending=False).tail(5), palette=colors2, ax=axes[0,1])
axes[0, 1].set_ylabel("Jumlah customer")
axes[0, 1].set_xlabel("State")
axes[0, 1].set_title("State dengan customer paling sedikit", loc="center", fontsize=15)
axes[0, 1].tick_params(axis='x', labelsize=15)

sns.barplot(y="total_customers", x="customer_city", data=customer_city_df.head(5), palette=colors, ax=axes[1,0])
axes[1, 0].set_ylabel("Jumlah customer")
axes[1, 0].set_xlabel("City")
axes[1, 0].set_title("City dengan customer paling banyak", loc="center", fontsize=15)
axes[1, 0].tick_params(axis='x', labelsize=15)

sns.barplot(y="total_customers", x="customer_city", data=customer_city_df.sort_values(by="total_customers", ascending=False).tail(5), palette=colors3, ax=axes[1,1])
axes[1, 1].set_ylabel("Jumlah customer")
axes[1, 1].set_xlabel("City")
axes[1, 1].set_title("City dengan customer paling sedikit", loc="center", fontsize=15)

st.pyplot(fig)

# # Pertanyaan 5
# st.subheader("Time Series")
# # Plot 1: Distribusi Order per Bulan
# fig, ax = plt.subplots(figsize=(16, 8))
# ax.plot(
#     orders_per_day,
#     marker='o', 
#     linewidth=2,
#     color="#90CAF9",
#     label="Jumlah Order"
# )
# ax.set_xlabel("Tanggal")
# ax.set_ylabel("Jumlah Order (qty)")
# ax.set_title("Jumlah Order per Hari")
# ax.tick_params(axis='y', labelsize=20)
# ax.tick_params(axis='x', labelsize=15)

# st.pyplot(fig)

# # Plot 2: Tren Penjualan Per Bulan

# fig, ax = plt.subplots(figsize=(16, 8))
# ax.plot(
#     sales_per_day,
#     marker='o', 
#     linewidth=2,
#     color="g",
#     label="Total Penjualan (payment value)"
# )
# ax.set_xlabel("Tanggal")
# ax.set_ylabel("Total Penjualan ($)")
# ax.set_title("Tren Penjualan")
# ax.tick_params(axis='y', labelsize=20)
# ax.tick_params(axis='x', labelsize=15)

# st.pyplot(fig)

# # Plot 3: Status Order per Bulan

# fig, ax = plt.subplots(figsize=(16, 8))
# ax.plot(
#     order_status_per_day,
#     # kind="bar",
#     # stacked=True,
#     # color=['gray', 'green', 'blue', 'orange', 'black', 'yellow', 'red', 'pink'],
#     label="Status Order per Bulan"
# )
# ax.set_xlabel("Tanggal")
# ax.set_ylabel("Jumlah Order")
# ax.set_title("Status Order")
# ax.tick_params(axis='y', labelsize=20)
# ax.tick_params(axis='x', labelsize=15)

# st.pyplot(fig)
