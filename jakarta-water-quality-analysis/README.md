# Jakarta Water Quality Analysis

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Jupyter](https://img.shields.io/badge/Jupyter-1.1-orange)

## 📌 Deskripsi
Exploratory Data Analysis (EDA) untuk data kualitas air Jakarta. Synthetic data 500 records dengan parameter: pH, turbidity, TDS, dissolved oxygen, temperature. Dibuat untuk Smart Water Management competition.

## 🎯 Fitur
- Generate synthetic water quality data (realistic ranges)
- Statistical summary & distribution analysis
- District comparison (5 wilayah Jakarta)
- Correlation heatmap
- Time series trend analysis
- Anomaly detection (outlier identification)

## 🛠️ Tech Stack
- Python, Jupyter, Pandas, Seaborn, Matplotlib

## 🚀 Cara Menjalankan

```bash
pip install -r requirements.txt
python data/generator.py
jupyter notebook notebook.ipynb
```

## 📊 Key Insight
- Jakarta Utara & Timur: pH rata-rata 6.5 (perlu alkalinitas)
- 12% sampel turbidity > 25 NTU (di atas standar WHO 5 NTU)
- Dissolved oxygen & temperature: korelasi negatif -0.65

## 👤 Author
[Avatar Putra Sigit](https://linkedin.com/in/avatarputrasigit) — Founder & CEO @AVA.Group
[GitHub](https://github.com/qurrrrsebastian-prog)
