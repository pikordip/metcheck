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
    df["Durum"] = df["Durum"].fillna("Unknown").str.strip()
    return df

# --- 📥 Veri Yükle ---
df = load_data(excel_path, sheet_name)

# --- 🎛️ Filtre: Agency Seçimi ---
st.sidebar.title("🔍 Filtreler")
firmalar = df["Firma"].dropna().unique().tolist()
secili_firma = st.sidebar.selectbox("Firma seçin", ["Tüm Firmalar"] + firmalar)

if secili_firma != "Tüm Firmalar":
    df = df[df["Firma"] == secili_firma]

# --- 📊 Pivot Tablosu Oluştur ---
pivot_df = df.pivot_table(index="Otel", columns="Durum", aggfunc="size", fill_value=0)
pivot_df["Toplam"] = pivot_df.sum(axis=1)

# --- 🧾 Genel Toplamlar ---
toplamlar = pivot_df.sum(axis=0)
ok_sayisi = int(toplamlar.get("Ok", 0))
iptal_sayisi = int(toplamlar.get("Cancelled", 0))
toplam_rezervasyon = int(toplamlar.get("Toplam", 0))

# --- 🧩 Başlık ve Metrikler ---
st.title("🏨 Otel Bazlı Satış Raporu")
st.subheader(f"📁 Firma: {secili_firma}")
st.markdown("### 🔸 Genel Rapor Özeti")

col1, col2, col3 = st.columns(3)
col1.metric("🟢 Satış (Ok)", ok_sayisi)
col2.metric("🔴 İptal (Cancelled)", iptal_sayisi)
col3.metric("📌 Toplam", toplam_rezervasyon)

# --- 📑 Detaylı Tablo Gösterimi ---
st.markdown("### 📊 Otel Detayları")
st.dataframe(pivot_df.sort_values(by="Toplam", ascending=False), use_container_width=True)
