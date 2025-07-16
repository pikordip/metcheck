import streamlit as st
import pandas as pd

# --- 📁 Dosya Yolu Ayarı ---
excel_path = "data/metbeds/NB_DATA.xlsx"
sheet_ana = "ana_data"
sheet_booking = "Product bookings"

# --- 🔁 Veri Yükleme Fonksiyonu ---
@st.cache_data
def load_data(path_ana, path_booking):
    ana_df = pd.read_excel(path_ana, sheet_name=sheet_ana)
    booking_df = pd.read_excel(path_booking, sheet_name=sheet_booking)

    # Temel sütunları yeniden adlandır
    ana_df = ana_df[[
        "Hotel", "JPCode", "Hotel Requests OK", "% Hotel Requests OK",
        "Total Hotel Requests", "Kategori", "SEÇ"
    ]].copy()
    ana_df.columns = [
        "Otel", "JPCode", "Sorgu_OK", "Sorgu_OK_Yuzde", "Toplam_Sorgu",
        "Kategori", "Firma"
    ]

    # Booking verisi temizleme
    booking_df = booking_df[["JP Code", "Agency", "Status by booking element"]].copy()
    booking_df.columns = ["JPCode", "Agency", "Durum"]
    booking_df["Durum"] = booking_df["Durum"].fillna("Unknown").str.strip().str.lower()

    # Her JPCode ve Firma için eşleşme yaparak rezervasyonları hesapla
    rez_list = []
    for _, row in ana_df.iterrows():
        jp = row["JPCode"]
        ag = row["Firma"]
        ilgili = booking_df[(booking_df["JPCode"] == jp) & (booking_df["Agency"] == ag)]
        ok = (ilgili["Durum"] == "ok").sum()
        cancelled = (ilgili["Durum"] == "cancelled").sum()
        toplam = len(ilgili)
        ok_yuzde = round(ok / toplam, 2) if toplam else 0
        cancelled_yuzde = round(cancelled / toplam, 2) if toplam else 0
        rez_list.append([ok, cancelled, toplam, ok_yuzde, cancelled_yuzde])

    ana_df[["Rez_OK", "Rez_Cancelled", "Rez_Toplam", "Rez_OK_Yuzde", "Rez_Cancelled_Yuzde"]] = rez_list

    return ana_df

# --- 📥 Veri Yükle ---
df = load_data(excel_path, excel_path)

# --- 🎛️ Sidebar Filtreler ---
st.sidebar.title("🔍 Filtreler")

kategori_list = sorted(df["Kategori"].dropna().unique())
secili_kategori = st.sidebar.selectbox("Kategori Seçin", ["Tüm Kategoriler"] + kategori_list)

firma_list = sorted(df["Firma"].dropna().unique())
secili_firma = st.sidebar.selectbox("Firma Seç", ["Tüm Firmalar"] + firma_list)

# --- 🔎 Filtreleri Uygula ---
if secili_kategori != "Tüm Kategoriler":
    df = df[df["Kategori"] == secili_kategori]
if secili_firma != "Tüm Firmalar":
    df = df[df["Firma"] == secili_firma]

# --- 🧾 Sayfa Başlığı ---
st.title("📊 Sorgu Analiz Raporu")
st.subheader(f"Kategori: {secili_kategori} | Firma: {secili_firma}")

# --- 📋 Gösterilecek Sütunlar ---
gosterilecek = df[[
    "Otel", "Sorgu_OK", "Toplam_Sorgu", "Sorgu_OK_Yuzde",
    "Rez_OK", "Rez_Cancelled", "Rez_Toplam", "Rez_OK_Yuzde", "Rez_Cancelled_Yuzde"
]].copy()

# Başlıkları daha okunur hale getir
gosterilecek.columns = [
    "Otel", "Hotel Requests OK", "Total Requests", "% Hotel Requests OK",
    "OK", "Cancelled", "Total Reservations", "OK %", "Cancelled %"
]

# --- 📑 Tablo Gösterimi ---
st.markdown("### 📌 Detaylı Otel Performansı")
st.dataframe(gosterilecek.sort_values(by="Total Reservations", ascending=False), use_container_width=True)
