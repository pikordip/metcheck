import streamlit as st
import pandas as pd

# --- 📁 Dosya Yolu Ayarı ---
excel_path = "data/NB_DATA.xlsx"
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

# --- 🎛️ Sidebar: Firma Filtresi ---
st.sidebar.title("🔍 Filtreler")
firmalar = df["Firma"].dropna().unique().tolist()
secili_firma = st.sidebar.selectbox("Firma seçin", ["Tüm Firmalar"] + firmalar)

if secili_firma != "Tüm Firmalar":
    df = df[df["Firma"] == secili_firma]

# --- 📊 Pivot Tablosu Oluştur ---
pivot_df = df.pivot_table(index="Otel", columns="Durum", aggfunc="size", fill_value=0)
pivot_df["Toplam"] = pivot_df.sum(axis=1)

# --- 📋 Sütunları özel sıralamayla yeniden düzenle ("ok", "cancelled", diğerleri)
preferred_order = ["ok", "cancelled"]
others = [col for col in pivot_df.columns if col not in preferred_order + ["Toplam"]]
new_order = preferred_order + others + ["Toplam"]
pivot_df = pivot_df.reindex(columns=new_order)

# --- 🧾 Genel Toplamlar ---
toplamlar = pivot_df.sum(axis=0)

# --- 🧩 Sayfa Başlığı ve Metrikler ---
st.title("🏨 Otel Bazlı Satış Raporu")
st.subheader(f"📁 Firma: {secili_firma}")
st.markdown("### 🔸 Genel Rapor Özeti")

cols = st.columns(len(toplamlar))
for i, durum in enumerate(toplamlar.index):
    etiket = durum.capitalize() if durum != "Toplam" else "Toplam"
    cols[i].metric(etiket, int(toplamlar[durum]))

# --- 📑 Detaylı Tablo Gösterimi ---
st.markdown("### 📊 Otel Detayları")
st.dataframe(pivot_df.sort_values(by="Toplam", ascending=False), use_container_width=True)
