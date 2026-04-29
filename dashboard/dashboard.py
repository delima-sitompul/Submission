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

st.set_page_config(
    page_title="Air Quality Beijing Dashboard",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 1.5rem; border-radius: 12px;
        color: white; text-align: center; margin: 4px;
    }
    .metric-card h2 { font-size: 2rem; margin: 0; }
    .metric-card p  { font-size: 0.85rem; margin: 0; opacity: 0.85; }
    .danger-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .good-card   { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .warn-card   { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    paths = ['main_data.csv', 'dashboard/main_data.csv', '../data/main_data.csv']
    for p in paths:
        if os.path.exists(p):
            return pd.read_csv(p, parse_dates=['datetime'])
    csv_files = glob.glob('PRSA_Data_20130301-20170228/*.csv')
    if not csv_files:
        csv_files = glob.glob('../PRSA_Data_20130301-20170228/*.csv')
    if csv_files:
        dfs = [pd.read_csv(f) for f in csv_files]
        df  = pd.concat(dfs, ignore_index=True)
        df['datetime'] = pd.to_datetime(df[['year','month','day','hour']])
        df = df.sort_values(['station','datetime']).reset_index(drop=True)
        num_cols = ['PM2.5','PM10','SO2','NO2','CO','O3','TEMP','PRES','DEWP','RAIN','WSPM']
        df[num_cols] = df.groupby('station')[num_cols].transform(
            lambda x: x.interpolate(method='linear', limit_direction='both'))
        for c in num_cols:
            df[c].fillna(df[c].median(), inplace=True)
        df['wd'].fillna('N', inplace=True)
        def season(m):
            return 'Spring' if m in [3,4,5] else 'Summer' if m in [6,7,8] \
                   else 'Autumn' if m in [9,10,11] else 'Winter'
        df['season'] = df['month'].map(season)
        def aqi(v):
            if pd.isna(v): return 'Unknown'
            elif v <= 12:   return 'Good'
            elif v <= 35.4: return 'Moderate'
            elif v <= 55.4: return 'Unhealthy (Sensitive)'
            elif v <= 150.4: return 'Unhealthy'
            elif v <= 250.4: return 'Very Unhealthy'
            else:            return 'Hazardous'
        df['AQI_Category'] = df['PM2.5'].apply(aqi)
        return df
    st.error("❌ File data tidak ditemukan.")
    st.stop()

df = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/air-quality.png", width=120)
    st.title("🌫️ Air Quality\nBeijing Dashboard")
    st.markdown("---")

    stations = sorted(df['station'].unique())
    selected_stations = st.multiselect("📍 Pilih Stasiun", stations, default=stations[:4])

    st.markdown("📅 **Rentang Tanggal**")
    min_date = df['datetime'].min().date()
    max_date = df['datetime'].max().date()
    start_date = st.date_input("Dari tanggal",  value=min_date, min_value=min_date, max_value=max_date)
    end_date   = st.date_input("Sampai tanggal", value=max_date, min_value=min_date, max_value=max_date)
    if start_date > end_date:
        st.error("⚠️ Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
        st.stop()

    seasons_list = ['Spring', 'Summer', 'Autumn', 'Winter']
    selected_seasons = st.multiselect("🍂 Musim", seasons_list, default=seasons_list)

    st.markdown("---")
    st.caption("Data: PRSA Beijing Air Quality (2013–2017)\nSource: UCI ML Repository")

# ── FILTER ────────────────────────────────────────────────────────────────────
mask = (
    df['station'].isin(selected_stations) &
    (df['datetime'].dt.date >= start_date) &
    (df['datetime'].dt.date <= end_date) &
    df['season'].isin(selected_seasons)
)
dff = df[mask]
if dff.empty:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    st.stop()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🌫️ Dashboard Kualitas Udara Beijing (2013–2017)")
st.markdown(
    f"Menampilkan data dari **{len(selected_stations)} stasiun** | "
    f"**{start_date.strftime('%d %b %Y')} – {end_date.strftime('%d %b %Y')}** | "
    f"Musim: **{', '.join(selected_seasons)}**"
)
st.markdown("---")

# ── KPI ───────────────────────────────────────────────────────────────────────
avg_pm25   = dff['PM2.5'].mean()
max_pm25   = dff['PM2.5'].max()
pct_danger = ((dff['PM2.5'] > 150.4).sum() / len(dff) * 100)
pct_good   = ((dff['PM2.5'] <= 12).sum()  / len(dff) * 100)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card warn-card"><p>Rata-rata PM2.5</p><h2>{avg_pm25:.1f}</h2><p>µg/m³</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card danger-card"><p>PM2.5 Tertinggi</p><h2>{max_pm25:.0f}</h2><p>µg/m³</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card danger-card"><p>% Waktu Berbahaya</p><h2>{pct_danger:.1f}%</h2><p>Very Unhealthy + Hazardous</p></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card good-card"><p>% Waktu Aman</p><h2>{pct_good:.1f}%</h2><p>PM2.5 ≤ 12 µg/m³ (Good)</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── PERTANYAAN 1 ──────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Pertanyaan 1: Bagaimana tren rata-rata konsentrasi PM2.5 (µg/m³) per musim di 12 stasiun pemantauan Beijing selama Maret 2013 – Februari 2017, dan stasiun mana yang secara konsisten mencatat kualitas udara terburuk berdasarkan rata-rata PM2.5 tahunan?")

col_a, col_b = st.columns([3, 2])
with col_a:
    st.markdown("**Tren Bulanan PM2.5 per Stasiun**")
    monthly_trend = dff.groupby(['year','month','station'])['PM2.5'].mean().reset_index()
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
    st.pyplot(fig); plt.close()

with col_b:
    st.markdown("**Rata-rata PM2.5 per Stasiun & Musim**")
    season_station = dff.groupby(['station','season'])['PM2.5'].mean().unstack(fill_value=0)
    s_pal = {'Spring':'#4CAF50','Summer':'#FF9800','Autumn':'#795548','Winter':'#2196F3'}
    fig3, ax3 = plt.subplots(figsize=(7, 4))
    x = np.arange(len(season_station)); width = 0.2
    for i, s in enumerate(['Spring','Summer','Autumn','Winter']):
        if s in season_station.columns:
            ax3.bar(x + i*width, season_station[s], width, label=s, color=s_pal[s], alpha=0.9, edgecolor='white')
    ax3.axhline(15, color='red', linestyle='--', linewidth=1.2, label='WHO 15')
    ax3.set_xticks(x + width*1.5)
    ax3.set_xticklabels(season_station.index, rotation=30, ha='right', fontsize=8)
    ax3.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=9)
    ax3.legend(fontsize=8)
    ax3.spines[['top','right']].set_visible(False)
    fig3.tight_layout()
    st.pyplot(fig3); plt.close()

# ── PERTANYAAN 2 ──────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Pertanyaan 2: Pada jam berapa dalam sehari dan bulan apa dalam setahun konsentrasi PM2.5 rata-rata mencapai puncaknya di seluruh stasiun pemantauan Beijing selama 2013–2017?")

col_c, col_d = st.columns(2)
with col_c:
    st.markdown("**Pola PM2.5 per Jam dalam Sehari**")
    hourly = dff.groupby('hour')['PM2.5'].mean()
    fig4, ax4 = plt.subplots(figsize=(7, 4))
    ax4.fill_between(hourly.index, hourly.values, alpha=0.3, color='#3498db')
    ax4.plot(hourly.index, hourly.values, color='#2980b9', linewidth=2.5, marker='o', markersize=4)
    ax4.axhspan(0, 15, alpha=0.1, color='green', label='Zona Aman WHO')
    ax4.set_xticks(range(0, 24, 2))
    ax4.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)], rotation=45, fontsize=7.5)
    ax4.set_xlabel('Jam', fontsize=10); ax4.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=10)
    ax4.legend(fontsize=9); ax4.spines[['top','right']].set_visible(False)
    peak_h = hourly.idxmax()
    ax4.annotate(f'Puncak {peak_h:02d}:00\n{hourly[peak_h]:.0f} µg/m³',
                 xy=(peak_h, hourly[peak_h]),
                 xytext=(peak_h - 6 if peak_h > 10 else peak_h + 2, hourly[peak_h] + 3),
                 arrowprops=dict(arrowstyle='->', color='#e74c3c'),
                 color='#e74c3c', fontsize=8, fontweight='bold')
    fig4.tight_layout(); st.pyplot(fig4); plt.close()

with col_d:
    st.markdown("**Rata-rata PM2.5 per Bulan**")
    monthly  = dff.groupby('month')['PM2.5'].mean()
    mn = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    bc = ['#2196F3' if m in [12,1,2] else '#FF9800' if m in [3,4,5]
          else '#4CAF50' if m in [6,7,8] else '#795548' for m in monthly.index]
    fig5, ax5 = plt.subplots(figsize=(7, 4))
    bars = ax5.bar(monthly.index, monthly.values, color=bc, edgecolor='white', width=0.7)
    ax5.set_xticks(range(1, 13))
    ax5.set_xticklabels([mn[m-1] for m in range(1, 13)], fontsize=9)
    ax5.set_xlabel('Bulan', fontsize=10); ax5.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=10)
    ax5.axhline(15, color='red', linestyle='--', linewidth=1.5, label='WHO 15 µg/m³')
    for bar, val in zip(bars, monthly.values):
        ax5.text(bar.get_x() + bar.get_width()/2, val + 0.5, f'{val:.0f}', ha='center', fontsize=7.5, fontweight='bold')
    leg = [Patch(color='#2196F3', label='Winter'), Patch(color='#FF9800', label='Spring'),
           Patch(color='#4CAF50', label='Summer'), Patch(color='#795548', label='Autumn')]
    ax5.legend(handles=leg, fontsize=8, loc='upper right')
    ax5.spines[['top','right']].set_visible(False)
    fig5.tight_layout(); st.pyplot(fig5); plt.close()

# ── HEATMAP ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("**Heatmap PM2.5 – Bulan × Jam**")
heat_data = dff.groupby(['month','hour'])['PM2.5'].mean().unstack()
mn = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
fig6, ax6 = plt.subplots(figsize=(14, 4))
cmap = LinearSegmentedColormap.from_list('aq', ['#2ecc71','#f1c40f','#e67e22','#e74c3c','#8e44ad'])
sns.heatmap(heat_data, ax=ax6, cmap=cmap, linewidths=0,
            cbar_kws={'label': 'Rata-rata PM2.5 (µg/m³)'},
            xticklabels=[f'{h:02d}:00' for h in range(24)],
            yticklabels=[mn[m-1] for m in heat_data.index])
ax6.set_xlabel('Jam dalam Sehari', fontsize=10)
ax6.set_ylabel('Bulan', fontsize=10)
ax6.tick_params(axis='x', rotation=45, labelsize=8)
fig6.tight_layout(); st.pyplot(fig6); plt.close()

# # ── AQI DISTRIBUTION ─────────────────────────────────────────────────────────
# st.markdown("---")
# col_e, col_f = st.columns(2)
# with col_e:
#     st.markdown("**Distribusi Kategori AQI**")
#     aqi_order  = ['Good','Moderate','Unhealthy (Sensitive)','Unhealthy','Very Unhealthy','Hazardous']
#     aqi_colors = ['#2ecc71','#f1c40f','#e67e22','#e74c3c','#9b59b6','#8e44ad']
#     aqi_counts = dff['AQI_Category'].value_counts().reindex(aqi_order, fill_value=0)

#     mask_aqi   = aqi_counts.values > 0
#     counts_fil = aqi_counts.values[mask_aqi]
#     labels_fil = [f'{aqi_order[i]}\n({aqi_counts.values[i]:,})' for i in range(len(aqi_order)) if mask_aqi[i]]
#     colors_fil = [aqi_colors[i] for i in range(len(aqi_order)) if mask_aqi[i]]

#     fig7, ax7 = plt.subplots(figsize=(5, 4))
#     ax7.pie(counts_fil, labels=labels_fil, colors=colors_fil,
#             autopct=lambda p: f'{p:.1f}%' if p > 3 else '',
#             startangle=90, pctdistance=0.75, textprops={'fontsize': 7})
#     ax7.set_title('Distribusi Kategori AQI', fontsize=11, fontweight='bold')
#     fig7.tight_layout(); st.pyplot(fig7); plt.close()

with col_f:
    st.markdown("**% Waktu Kondisi Berbahaya per Stasiun**")
    danger_pct = (
        dff[dff['PM2.5'] > 150.4].groupby('station').size() /
        dff.groupby('station').size() * 100
    ).fillna(0).sort_values(ascending=True)
    fig8, ax8 = plt.subplots(figsize=(6, 4))
    colors_d = ['#e74c3c' if v > 20 else '#e67e22' if v > 10 else '#f1c40f' for v in danger_pct.values]
    ax8.barh(danger_pct.index, danger_pct.values, color=colors_d, edgecolor='white', height=0.6)
    for i, val in enumerate(danger_pct.values):
        ax8.text(val + 0.2, i, f'{val:.1f}%', va='center', fontsize=8)
    ax8.set_xlabel('% Waktu Berbahaya (PM2.5 > 150 µg/m³)', fontsize=9)
    ax8.spines[['top','right']].set_visible(False)
    fig8.tight_layout(); st.pyplot(fig8); plt.close()

st.markdown("---")
st.caption("Dashboard dibuat menggunakan Streamlit | Data: PRSA Air Quality Dataset Beijing 2013–2017")
