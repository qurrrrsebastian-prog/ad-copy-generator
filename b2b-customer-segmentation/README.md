# B2B Customer Segmentation ⭐ Bintang 5 — Slate Corporate

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58-red)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.9-orange)
![Theme](https://img.shields.io/badge/Theme-Slate%20Corporate-fb7185)

## 📌 Deskripsi
AI-powered **K-Means clustering** untuk segmentasi klien B2B dan optimasi customer
lifetime value. Data dummy 200 records, 4 segmen bisnis (Champions / Loyal /
At Risk / Lost), dengan UI glassmorphism bertema **Slate Corporate** (coral accent).

## 🎯 Fitur
- K-Means clustering (4 segmen) + pelabelan otomatis berbasis centroid
- **Fallback rule-based** bila K-Means gagal konvergen
- KPI cards per segmen (gold / green / orange / red), glassmorphism
- Tabs: Segments (pie + bar + summary), Scatter Plot (revenue × engagement),
  Client List (search + filter), At Risk (recommended actions)
- Download CSV per segmen (nama perusahaan di-mask untuk privasi)
- History run tersimpan di SQLite, rate-limit 5 run/sesi
- Mobile responsive (KPI 2×2, tabel horizontal scroll)

## 🔒 Security
- `sanitize_input` (strip HTML, max 500 char, XSS-safe)
- `validate_numeric` / `validate_select` (range & membership)
- Parameterized SQL queries, session ID, data masking (demo mode)

## 🛠️ Tech Stack
Python · Streamlit · Scikit-learn · Plotly · Pandas · NumPy · SQLite

## 📂 Struktur
```
app.py                  # Dashboard utama (Slate Corporate)
core/
  ├─ database.py        # init_db, save_segmentation, get_history
  ├─ security.py        # sanitize, validate, session, mask
  └─ theme.py           # CSS Slate Corporate + skeleton + responsive
data/
  ├─ seeder.py          # 200 klien + K-Means pre-labeling
  └─ generator.py       # generator lama (dipertahankan)
.streamlit/config.toml  # tema dark coral
```

## 🚀 Cara Menjalankan
```bash
pip install -r requirements.txt
python data/seeder.py      # generate data/clients.csv
streamlit run app.py
```

## 📊 Key Insight
- **Champions** (revenue & engagement tinggi): prioritaskan retensi & upsell premium
- **At Risk** (recency tinggi / engagement turun): outreach personal + diskon
- **Lost**: kampanye win-back atau lepas dengan biaya rendah

## 👤 Author
[Avatar Putra Sigit](https://linkedin.com/in/avatarputrasigit) — Founder & CEO @AVA.Group
[GitHub](https://github.com/qurrrrsebastian-prog)
