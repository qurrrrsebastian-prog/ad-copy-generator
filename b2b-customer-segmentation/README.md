# B2B Customer Segmentation

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58-red)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.8-orange)

## 📌 Deskripsi
K-Means clustering untuk segmentasi klien B2B jasa property maintenance. Data dummy 200 records dengan 6 fitur bisnis. Output: persona cluster + rekomendasi marketing per segment.

## 🎯 Fitur
- Elbow method untuk cari K optimal
- K-Means clustering interaktif
- PCA 2D visualization (Plotly)
- Auto persona labeling: High-Value Loyal, At-Risk Big Client, Small Frequent, New Potential
- Recommendation engine per cluster

## 🛠️ Tech Stack
- Python, Streamlit, Scikit-learn, Plotly, Pandas

## 🚀 Cara Menjalankan

```bash
pip install -r requirements.txt
python data/generator.py
streamlit run app.py
```

## 📊 Key Insight
- 20-25% klien adalah High-Value Loyal (kontrak > Rp 80jt, satisfaction > 4.2)
- At-Risk Big Client perlu immediate outreach (kontrak besar tapi last order > 180 hari)
- Small Frequent bisa di-upsell ke annual contract

## 👤 Author
[Avatar Putra Sigit](https://linkedin.com/in/avatarputrasigit) — Founder & CEO @AVA.Group
[GitHub](https://github.com/qurrrrsebastian-prog)
