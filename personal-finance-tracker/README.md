# Personal Finance Tracker

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58-ff4b4b)
![Theme](https://img.shields.io/badge/Theme-Sage%20Mint-2dd4bf)

## 📌 Deskripsi
Web app untuk tracking pemasukan & pengeluaran pribadi. **Streamlit + SQLite + Plotly**
dengan tema **Sage Mint** (glassmorphism, KPI cards, analytics dashboard). Data
tersimpan di database lokal `finance.db`.

> Versi Flask lama disimpan di folder `old_app/` (tidak dihapus).

## 🎯 Fitur
- Form transaksi (Pemasukan/Pengeluaran) di sidebar dengan validasi penuh
- 4 KPI cards: Pemasukan, Pengeluaran, Saldo, Pengeluaran terbesar (delta MoM)
- **Dashboard**: pie kategori, bar income vs expense, tren saldo harian
- **Trends**: pengeluaran mingguan, tren kategori, gauge tingkat tabungan
- **Transaksi**: tabel sortable, warna baris, hapus, export CSV
- **Kalender**: heatmap intensitas pengeluaran 90 hari + drilldown per tanggal
- Keamanan: sanitasi input/XSS, validasi jumlah & tanggal, anti-duplikat, rate limit
- Format Rupiah otomatis (Rp 1.000.000), empty state, toast, responsive

## 🛠️ Tech Stack
Python · Streamlit · SQLite · Plotly · pandas · numpy

## 📂 Struktur
```
app.py                 # UI utama Streamlit
core/database.py       # SQLite (parameterized queries, migrasi schema)
core/security.py       # sanitasi & validasi input
core/theme.py          # CSS Sage Mint + format Rupiah
data/seeder.py         # 100 transaksi dummy (seed=42)
.streamlit/config.toml # tema dasar
old_app/               # backup versi Flask
```

## 🚀 Cara Menjalankan
```bash
pip install -r requirements.txt
streamlit run app.py
```
Buka browser: http://localhost:8501

Database kosong akan otomatis di-seed 100 transaksi demo. Untuk re-seed manual:
```bash
python -m data.seeder
```

## 📊 Key Insight
- Tracking expense harian mengurangi pengeluaran impulsif 20-30%
- Kategori terbesar biasanya "Makan" & "Transport" untuk mahasiswa
- SQLite cukup untuk personal finance < 10,000 transaksi

## 👤 Author
[Avatar Putra Sigit](https://linkedin.com/in/avatarputrasigit) — Founder & CEO @AVA.Group
[GitHub](https://github.com/qurrrrsebastian-prog)
