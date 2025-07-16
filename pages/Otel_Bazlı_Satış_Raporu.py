import streamlit as st
import pandas as pd

# --- 📁 Dosya Yolu Ayarı ---
excel_path = "data/metbeds/NB_DATA.xlsx"
sheet_name = "Product bookings"

# --- 🔁 Veri Yükleme Fonksiyonu ---
@st.cache_data
def load_data(path, sheet):
    df = pd.read_excel(path, sheet_name=sheet)
    df = df[["Accommodation Name", "Agency", "Status by booking element"]]
    df.columns = ["Otel", "Firma", "Durum"]
    df["Durum"] = df["Durum"].fillna("Unknown").str.strip().str.lower()
    return df

# --- 📥 Veri Yükle ---
df = load_data(excel_path, sheet_name)

# --- 🎛️ Sidebar: Agency Seçimi ---
st.sidebar.title("🔍 Filtreler")
firmalar = df["Firma"].dropna().unique().tolist()
secili_firma = st.sidebar.selectbox("Firma seçin", ["Tüm Firmalar"] + firmalar)

if secili_firma != "Tüm Firmalar":
    df = df[df["Firma"] == secili_firma]

# --- 📊 Pivot Tablosu Oluştur ---
pivot_df = df.pivot_table(index="Otel", columns="Durum", aggfunc="size", fill_value=0)

# --- ➕ Toplam Kolonu ---
pivot_df["toplam"] = pivot_df.sum(axis=1)

# --- 📋 Statüleri Belirli Sıralamayla Göster ("ok" → "cancelled" → diğerleri)
preferred_order = ["ok", "cancelled"]
remaining = [col for col in pivot_df.columns if col not in preferred_order + ["toplam"]]
new_order = preferred_order + remaining + ["toplam"]
pivot_df = pivot_df.reindex(columns=new_order)

# --- 🧾 Genel Toplamlar ---
toplamlar = pivot_df.sum(axis=0)

# --- 🧩 Sayfa Başlığı ve Özet Metrikler ---
st.title("🏨 Otel Bazlı Satış Raporu")
st.subheader(f"📁 Firma: {secili_firma}")
st.markdown("### 🔸 Genel Rapor Özeti")

cols = st.columns(len(toplamlar))
for i, durum in enumerate(toplamlar.index):
    etiket = durum.capitalize() if durum != "toplam" else "Toplam"
    cols[i].metric(etiket, int(toplamlar[durum]))

# --- 📑 Detaylı Tablo Gösterimi ---
st.markdown("### 📊 Otel Detayları")
st.dataframe(pivot_df.sort_values(by="toplam", ascending=False), use_container_width=True)
