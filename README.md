# Proyek Analisis Data: E-Commerce Public Dataset

## Deskripsi Proyek
Proyek ini bertujuan untuk menganalisis data *e-commerce* dari Olist Store (Brasil) guna mengungkap wawasan bisnis yang berharga. Analisis mencakup eksplorasi data (*Exploratory Data Analysis*), visualisasi tren penjualan, kinerja kategori produk, serta segmentasi pelanggan menggunakan analisis RFM (*Recency, Frequency, Monetary*).

Hasil analisis disajikan dalam bentuk *dashboard* interaktif menggunakan **Streamlit** untuk memudahkan pemangku kepentingan dalam memantau performa bisnis.

## Dataset
Dataset yang digunakan adalah **Brazilian E-Commerce Public Dataset by Olist** yang tersedia di Kaggle. Dataset ini mencakup informasi mengenai 100k pesanan dari tahun 2016 hingga 2018.
- Sumber: [Kaggle - Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

## Setup Environment - Shell/Terminal
```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
