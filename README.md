# Air Quality Analysis Dashboard 🌫️
### Beijing Air Quality Data (2013–2017)

Proyek analisis data kualitas udara Beijing menggunakan dataset PRSA dari 12 stasiun pemantauan. Proyek ini dibuat sebagai submission akhir kelas **Belajar Analisis Data dengan Python** di Dicoding.

---

## 🔗 Live Dashboard

👉 **[Buka Dashboard](https://submission-njr5pvbzuju8rbizdbal5v.streamlit.app/#898)**

---

## 📁 Struktur Direktori

```
Submission/
├── dashboard/
│   ├── dashboard.py        # Script Streamlit dashboard
│   └── main_data.csv       # Dataset bersih hasil proses cleaning
├── data/
│   └── PRSA_Data_20130301-20170228/
│       ├── PRSA_Data_Aotizhongxin_20130301-20170228.csv
│       ├── PRSA_Data_Changping_20130301-20170228.csv
│       ├── PRSA_Data_Dingling_20130301-20170228.csv
│       ├── PRSA_Data_Dongsi_20130301-20170228.csv
│       ├── PRSA_Data_Guanyuan_20130301-20170228.csv
│       ├── PRSA_Data_Gucheng_20130301-20170228.csv
│       ├── PRSA_Data_Huairou_20130301-20170228.csv
│       ├── PRSA_Data_Nongzhanguan_20130301-20170228.csv
│       ├── PRSA_Data_Shunyi_20130301-20170228.csv
│       ├── PRSA_Data_Tiantan_20130301-20170228.csv
│       ├── PRSA_Data_Wanliu_20130301-20170228.csv
│       └── PRSA_Data_Wanshouxigong_20130301-20170228.csv
├── notebook.ipynb          # Jupyter Notebook analisis lengkap (sudah dirun)
├── README.md
├── requirements.txt
└── url.txt
```

---

## 📊 Pertanyaan Bisnis

1. **Bagaimana tren rata-rata konsentrasi PM2.5 per musim di 12 stasiun pemantauan Beijing selama Maret 2013 – Februari 2017, dan stasiun mana yang secara konsisten mencatat kualitas udara terburuk?**

2. **Pada jam berapa dalam sehari dan bulan apa dalam setahun konsentrasi PM2.5 rata-rata mencapai puncaknya di seluruh stasiun pemantauan Beijing selama 2013–2017?**

---

## 🚀 Cara Menjalankan Dashboard di Local

### 1. Clone repository
```bash
git clone https://github.com/delima-sitompul/Submission.git
cd Submission
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Jalankan dashboard
```bash
streamlit run dashboard/dashboard.py
```

Dashboard akan otomatis terbuka di browser pada `http://localhost:8501`.

---

## 📦 Dataset

- **Sumber:** [PRSA Air Quality Dataset – UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data)
- **Periode:** Maret 2013 – Februari 2017
- **Jumlah stasiun:** 12 stasiun pemantauan di Beijing
- **Jumlah data:** ±420.768 baris (data per jam)
- **Fitur utama:** PM2.5, PM10, SO2, NO2, CO, O3, TEMP, PRES, DEWP, RAIN, WSPM

---

## 🛠️ Library yang Digunakan

| Library | Kegunaan |
|---|---|
| `pandas` | Manipulasi dan analisis data |
| `numpy` | Komputasi numerik |
| `matplotlib` | Visualisasi data |
| `seaborn` | Visualisasi statistik |
| `streamlit` | Pembuatan dashboard interaktif |
