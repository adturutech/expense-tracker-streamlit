# 💸 Expense Tracker (Rupiah Version)

A simple daily expense & income tracker built using **Python**, **Streamlit**, and **SQLite**.

## 🚀 Features
- Tambah transaksi (pemasukan/pengeluaran)
- Edit & hapus transaksi
- Filter berdasarkan tanggal & kategori
- Ringkasan pemasukan/pengeluaran/saldo
- Grafik pengeluaran bulanan
- Download CSV
- Format Rupiah otomatis (Rp 1.000.000)
- Timestamp WIB (UTC+07)

## 📦 Tech Stack
- Python 3.x
- Streamlit
- Pandas
- SQLite3

## 🛠 Cara Menjalankan
```bash
git clone https://github.com/<username>/expense-tracker.git
cd expense-tracker
python -m venv venv
source venv/bin/activate        # Mac/Linux
.\venv\Scripts\activate         # Windows
pip install -r requirements.txt
streamlit run app.py
