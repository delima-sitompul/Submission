import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
import glob, os, warnings

warnings.filterwarnings('ignore')

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Air Quality Beijing Dashboard",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 4px;
    }
    .metric-card h2 { font-size: 2rem; margin: 0; }
    .metric-card p  { font-size: 0.85rem; margin: 0; opacity: 0.85; }
    .danger-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .good-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .warn-card {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
    }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # Coba beberapa path umum
    paths = [
        'main_data.csv',
        'dashboard/main_data.csv',
        '../data/main_data.csv',
    ]
    for p in paths:
        if os.path.exists(p):
            return pd.read_csv(p, parse_dates=['datetime'])

    # Fallback: baca dari folder data jika tersedia
    csv_files = glob.glob('PRSA_Data_20130301-20170228/*.csv')
    if not csv_files:
        csv_files = glob.glob('../PRSA_Data_20130301-20170228/*.csv')
    if csv_files:
        dfs = [pd.read_csv(f) for f in csv_files]
        df = pd.concat(dfs, ignore_index=True)
        df['datetime'] = pd.to_datetime(df[['year','month','day','hour']])
        df = df.sort_values(['station','datetime']).reset_index(drop=True)
        # Quick impute
        num_cols = ['PM2.5','PM10','SO2','NO2','CO','O3','TEMP','PRES','DEWP','RAIN','WSPM']
        df[num_cols] = df.groupby('station')[num_cols].transform(
            lambda x: x.interpolate(method='linear', limit_direction='both'))
        for c in num_cols:
            df[c].fillna(df[c].median(), inplace=True)
        df['wd'].fillna('N', inplace=True)
        # Features
        def season(m):
            return 'Spring' if m in [3,4,5] else 'Summer' if m in [6,7,8] \
                   else 'Autumn' if m in [9,10,11] else 'Winter'
        df['season'] = df['month'].map(season)
        def aqi(v):
            if pd.isna(v): return 'Unknown'
            elif v <= 12:  return 'Good'
            elif v <= 35.4: return 'Moderate'
            elif v <= 55.4: return 'Unhealthy (Sensitive)'
            elif v <= 150.4: return 'Unhealthy'
            elif v <= 250.4: return 'Very Unhealthy'
            else: return 'Hazardous'
        df['AQI_Category'] = df['PM2.5'].apply(aqi)
        return df
    st.error(" File data tidak ditemukan. Pastikan main_data.csv ada di folder dashboard/")
    st.stop()

df = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/air-quality.png", width=120)
    st.title("🌫️ Air Quality\nBeijing Dashboard")
    st.markdown("---")

    stations = sorted(df['station'].unique())
    selected_stations = st.multiselect(
        "📍 Pilih Stasiun", stations, default=stations[:4]
    )

    year_min, year_max = int(df['year'].min()), int(df['year'].max())
    year_range = st.slider("📅 Rentang Tahun", year_min, year_max, (year_min, year_max))

    seasons = ['Spring', 'Summer', 'Autumn', 'Winter']
    selected_seasons = st.multiselect("🍂 Musim", seasons, default=seasons)

    st.markdown("---")
    st.caption("Data: PRSA Beijing Air Quality (2013–2017)\nSource: UCI ML Repository")

# ── FILTER DATA ───────────────────────────────────────────────────────────────
mask = (
    df['station'].isin(selected_stations) &
    df['year'].between(year_range[0], year_range[1]) &
    df['season'].isin(selected_seasons)
)
dff = df[mask]

if dff.empty:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    st.stop()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🌫️ Dashboard Kualitas Udara Beijing (2013–2017)")
st.markdown(f"Menampilkan data dari **{len(selected_stations)} stasiun** | "
            f"Tahun **{year_range[0]}–{year_range[1]}** | "
            f"Musim: **{', '.join(selected_seasons)}**")
st.markdown("---")

# ── KPI METRICS ───────────────────────────────────────────────────────────────
avg_pm25   = dff['PM2.5'].mean()
max_pm25   = dff['PM2.5'].max()
pct_danger = ((dff['PM2.5'] > 150.4).sum() / len(dff) * 100)
pct_good   = ((dff['PM2.5'] <= 12).sum() / len(dff) * 100)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="metric-card warn-card">
        <p>Rata-rata PM2.5</p><h2>{avg_pm25:.1f}</h2><p>µg/m³</p></div>""",
        unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card danger-card">
        <p>PM2.5 Tertinggi</p><h2>{max_pm25:.0f}</h2><p>µg/m³</p></div>""",
        unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card danger-card">
        <p>% Waktu Berbahaya</p><h2>{pct_danger:.1f}%</h2><p>Very Unhealthy + Hazardous</p></div>""",
        unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card good-card">
        <p>% Waktu Aman</p><h2>{pct_good:.1f}%</h2><p>PM2.5 ≤ 12 µg/m³ (Good)</p></div>""",
        unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CHART ROW 1 ───────────────────────────────────────────────────────────────
col_a, col_b = st.columns([3, 2])

with col_a:
    st.subheader("📈 Tren Bulanan PM2.5 per Stasiun")
    monthly_trend = (
        dff.groupby(['year','month','station'])['PM2.5'].mean().reset_index()
    )
    monthly_trend['date'] = pd.to_datetime(monthly_trend[['year','month']].assign(day=1))

    fig, ax = plt.subplots(figsize=(9, 4))
    palette = sns.color_palette("tab10", len(selected_stations))
    for i, st_name in enumerate(selected_stations):
        sub = monthly_trend[monthly_trend['station'] == st_name]
        ax.plot(sub['date'], sub['PM2.5'], label=st_name, color=palette[i], linewidth=1.8, alpha=0.85)
    ax.axhline(15, color='red', linestyle='--', linewidth=1.2, label='WHO 15 µg/m³')
    ax.set_xlabel('Tanggal', fontsize=10)
    ax.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=10)
    ax.legend(fontsize=7.5, ncol=2)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_b:
    st.subheader("🍩 Distribusi AQI Category")
    aqi_order  = ['Good','Moderate','Unhealthy (Sensitive)','Unhealthy','Very Unhealthy','Hazardous']
    aqi_colors = ['#2ecc71','#f1c40f','#e67e22','#e74c3c','#9b59b6','#8e44ad']
    aqi_counts = dff['AQI_Category'].value_counts().reindex(aqi_order, fill_value=0)

    fig2, ax2 = plt.subplots(figsize=(5, 4))
    wedges, texts, autotexts = ax2.pie(
        aqi_counts.values,
        labels=[f'{l}\n({v:,})' for l, v in zip(aqi_order, aqi_counts.values)],
        colors=aqi_colors,
        autopct=lambda p: f'{p:.1f}%' if p > 3 else '',
        startangle=90,
        pctdistance=0.75,
        textprops={'fontsize': 7}
    )
    ax2.set_title('Distribusi Kategori AQI', fontsize=11, fontweight='bold')
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close()

# ── CHART ROW 2 ───────────────────────────────────────────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("🏙️ Perbandingan PM2.5 antar Stasiun & Musim")
    season_station = (
        dff.groupby(['station','season'])['PM2.5'].mean().unstack(fill_value=0)
    )
    s_palette = {'Spring':'#4CAF50','Summer':'#FF9800','Autumn':'#795548','Winter':'#2196F3'}
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    x = np.arange(len(season_station))
    width = 0.2
    for i, s in enumerate(['Spring','Summer','Autumn','Winter']):
        if s in season_station.columns:
            ax3.bar(x + i*width, season_station[s], width, label=s,
                    color=s_palette[s], alpha=0.9, edgecolor='white')
    ax3.axhline(15, color='red', linestyle='--', linewidth=1.2, label='WHO 15')
    ax3.set_xticks(x + width*1.5)
    ax3.set_xticklabels(season_station.index, rotation=30, ha='right', fontsize=8)
    ax3.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=9)
    ax3.legend(fontsize=8)
    ax3.spines[['top','right']].set_visible(False)
    fig3.tight_layout()
    st.pyplot(fig3)
    plt.close()

with col_d:
    st.subheader("⏰ Pola PM2.5 per Jam dalam Sehari")
    hourly = dff.groupby('hour')['PM2.5'].mean()
    fig4, ax4 = plt.subplots(figsize=(7, 4))
    ax4.fill_between(hourly.index, hourly.values, alpha=0.3, color='#3498db')
    ax4.plot(hourly.index, hourly.values, color='#2980b9', linewidth=2.5,
             marker='o', markersize=4)
    ax4.axhspan(0, 15, alpha=0.1, color='green', label='Zona Aman WHO')
    ax4.set_xticks(range(0, 24, 2))
    ax4.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)], rotation=45, fontsize=7.5)
    ax4.set_xlabel('Jam', fontsize=10)
    ax4.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=10)
    ax4.legend(fontsize=9)
    ax4.spines[['top','right']].set_visible(False)
    peak_h = hourly.idxmax()
    ax4.annotate(f'Puncak {peak_h:02d}:00\n{hourly[peak_h]:.0f} µg/m³',
                 xy=(peak_h, hourly[peak_h]),
                 xytext=(peak_h - 6 if peak_h > 10 else peak_h + 2, hourly[peak_h] + 3),
                 arrowprops=dict(arrowstyle='->', color='#e74c3c'),
                 color='#e74c3c', fontsize=8, fontweight='bold')
    fig4.tight_layout()
    st.pyplot(fig4)
    plt.close()

# ── HEATMAP ───────────────────────────────────────────────────────────────────
st.subheader("🗓️ Heatmap PM2.5 – Bulan × Jam")
heat_data = dff.groupby(['month','hour'])['PM2.5'].mean().unstack()
month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

fig5, ax5 = plt.subplots(figsize=(14, 4))
cmap = LinearSegmentedColormap.from_list('aq', ['#2ecc71','#f1c40f','#e67e22','#e74c3c','#8e44ad'])
sns.heatmap(heat_data, ax=ax5, cmap=cmap, linewidths=0,
            cbar_kws={'label': 'Rata-rata PM2.5 (µg/m³)'},
            xticklabels=[f'{h:02d}:00' for h in range(24)],
            yticklabels=[month_names[m-1] for m in heat_data.index])
ax5.set_xlabel('Jam dalam Sehari', fontsize=10)
ax5.set_ylabel('Bulan', fontsize=10)
ax5.tick_params(axis='x', rotation=45, labelsize=8)
fig5.tight_layout()
st.pyplot(fig5)
plt.close()

# ── RAW DATA ──────────────────────────────────────────────────────────────────
with st.expander("🔍 Lihat Data Mentah (100 baris pertama)"):
    st.dataframe(dff[['datetime','station','PM2.5','PM10','SO2','NO2',
                       'CO','O3','TEMP','season','AQI_Category']].head(100),
                 use_container_width=True)

st.markdown("---")
st.caption("Dashboard dibuat menggunakan Streamlit | Data: PRSA Air Quality Dataset Beijing 2013–2017")
