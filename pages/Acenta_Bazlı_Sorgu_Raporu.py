import streamlit as st
import pandas as pd

# --- 📁 Dosya Yolları ---
excel_path = "data/metbeds/NB_DATA.xlsx"
alt_sheet = "alt_data"
booking_sheet = "Product bookings"

@st.cache_data
def load_data():
    # Alt veri sayfası
    alt_df = pd.read_excel(excel_path, sheet_name=alt_sheet)
    # Product bookings sayfası
    booking_df = pd.read_excel(excel_path, sheet_name=booking_sheet)
    
    # Sadece Agency olan firmaları filtrele
    acenta_firmalar = alt_df[alt_df["FİRMA"] == "Agency"].copy()

    # Temizle ve yeniden adlandır
    acenta_firmalar = acenta_firmalar[[
        "Sayfa İsmi", "Hotel", "Total Hotel Requests", "Hotel Requests OK", "JP Code"
    ]]
    acenta_firmalar.columns = ["Sayfa", "Otel", "Sorgu", "Başarılı Sorgu", "JPCode"]
    acenta_firmalar["Ajans"] = acenta_firmalar["Sayfa"]  # Ajans adı olarak ele al

    # Başarı oranı hesapla
    acenta_firmalar["Sorgu Başarı %"] = (
        acenta_firmalar["Başarılı Sorgu"] / acenta_firmalar["Sorgu"]
    ).fillna(0).round(2)

    # --- 🔗 Booking verileri ile JPCode ve Agency eşleştir ---
    booking_df = booking_df[["JP Code", "Agency", "Status by booking element"]]
    booking_df.columns = ["JPCode", "Ajans", "Durum"]
    booking_df["Durum"] = booking_df["Durum"].fillna("Unknown").str.strip().str.lower()

    # Her kayıt için eşleşen rezervasyonları filtrele
    rez_list = []
    for idx, row in acenta_firmalar.iterrows():
        jp = row["JPCode"]
        ag = row["Ajans"]
        ilgili = booking_df[
            (booking_df["JPCode"] == jp) & 
            (booking_df["Ajans"] == ag)
        ]
        ok = (ilgili["Durum"] == "ok").sum()
        cancelled = (ilgili["Durum"] == "cancelled").sum()
        toplam = len(ilgili)
        ok_orani = round(ok / toplam, 2) if toplam else 0
        iptal_orani = round(cancelled / toplam, 2) if toplam else 0
        rez_list.append([ok, cancelled, toplam, ok_orani, iptal_orani])

    # Yeni sütunlar ekle
    acenta_firmalar[["Rez_OK", "Rez_Cancelled", "Rez_Toplam", "Rez_OK %", "Rez_Cancelled %"]] = rez_list

    return acenta_firmalar

# --- 📥 Veri Yükle ---
df = load_data()

# --- 🎛️ Acenta Filtresi ---
st.sidebar.title("🔍 Filtreler")
ajanslar = sorted(df["Ajans"].unique())
secili_ajans = st.sidebar.selectbox("Acenta Seçin", ["Tüm Acentalar"] + ajanslar)

if secili_ajans != "Tüm Acentalar":
    df = df[df["Ajans"] == secili_ajans]

# --- 📋 Başlık ---
st.title("🏢 Acenta Bazlı Sorgu Raporu")
st.markdown("### 🔎 Sorgu ve Rezervasyon Başarıları")

# --- 📊 Detaylı Tablo Gösterimi ---
gosterilecek = df[[
    "Otel", "Sorgu", "Başarılı Sorgu", "Sorgu Başarı %",
    "Rez_OK", "Rez_Cancelled", "Rez_Toplam", "Rez_OK %", "Rez_Cancelled %"
]]

st.dataframe(gosterilecek.sort_values(by="Rez_Toplam", ascending=False), use_container_width=True)
