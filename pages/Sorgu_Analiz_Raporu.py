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

    # Sütunları sadeleştir ve yeniden adlandır
    ana_df = ana_df[[
        "Hotel", "JPCode", "Hotel Requests OK", "% Hotel Requests OK",
        "Total Hotel Requests", "Kategori", "SEÇ"
    ]].copy()
    ana_df.columns = [
        "Otel", "JPCode", "Sorgu_OK", "Yuzdelik_Sorgu_OK", "Toplam_Sorgu",
        "Kategori", "Firma"
    ]

    # % Hotel Requests OK oranını kendimiz hesaplıyoruz
    ana_df["Sorgu_OK_Yuzde"] = (
        ana_df["Sorgu_OK"] / ana_df["Toplam_Sorgu"]
    ).fillna(0).round(4)

    # Booking verisi: JPCode ve Durum
    booking_df = booking_df[["JP Code", "Agency", "Status by booking element"]].copy()
    booking_df.columns = ["JPCode", "Agency", "Durum"]
    booking_df["Durum"] = booking_df["Durum"].fillna("Unknown").str.strip().str.lower()

    # Her JPCode ve Firma için rezervasyonları eşleştir
    rez_list = []
    for _, row in ana_df.iterrows():
        jp = row["JPCode"]
        ag = row["Firma"]
        ilgili = booking_df[(booking_df["JPCode"] == jp) & (booking_df["Agency"] == ag)]
        ok = (ilgili["Durum"] == "ok").sum()
        cancelled = (ilgili["Durum"] == "cancelled").sum()
        toplam = ok + cancelled
        iptal_orani = round(cancelled / toplam, 4) if toplam else 0
        rez_list.append([ok, cancelled, toplam, iptal_orani])

    ana_df[["Rez_OK", "Rez_Cancelled", "Rez_Toplam", "Toplam_Iptal_Orani"]] = rez_list

    return ana_df

# --- 📥 Veri Yükle ---
df = load_data(excel_path, excel_path)

# --- 🎛️ Sidebar Entegre Filtreler ---
st.sidebar.title("🔍 Filtreler")

kategori_list = sorted(df["Kategori"].dropna().unique())
secili_kategori = st.sidebar.selectbox("Kategori Seçin (zorunlu)", kategori_list)

# Kategori seçildiyse sadece o kategorideki firmalar listelenir
firma_filtre = df[df["Kategori"] == secili_kategori]["Firma"].dropna().unique()
firma_list = sorted(firma_filtre)
secili_firma = st.sidebar.selectbox("Firma Seç", firma_list)

# --- 🔎 Filtreleri Uygula ---
df_filtreli = df[(df["Kategori"] == secili_kategori) & (df["Firma"] == secili_firma)]

# --- 📄 Sayfa Başlığı ---
st.title("📊 Sorgu Analiz Raporu")
st.subheader(f"Kategori: {secili_kategori} | Firma: {secili_firma}")

# --- 📋 Gösterilecek Alanlar ---
gosterilecek = df_filtreli[[
    "Otel", "Sorgu_OK", "Toplam_Sorgu", "Sorgu_OK_Yuzde",
    "Rez_OK", "Rez_Cancelled", "Rez_Toplam", "Toplam_Iptal_Orani"
]].copy()

# Başlıkları daha okunur hale getir
gosterilecek.columns = [
    "Otel", "Hotel Requests OK", "Total Requests", "% Hotel Requests OK",
    "OK", "Cancelled", "Total Reservations", "Total Cancelled %"
]

# --- ⛑️ Tip dönüşümleri (güvenli biçimlendirme için)
for col in [
    "Hotel Requests OK", "Total Requests", "OK", "Cancelled", "Total Reservations",
    "% Hotel Requests OK", "Total Cancelled %"
]:
    gosterilecek[col] = pd.to_numeric(gosterilecek[col], errors="coerce")

# --- 📊 Biçimlenmiş Tablo Gösterimi ---
st.markdown("### 📌 Detaylı Otel Performansı")

st.dataframe(
    gosterilecek.sort_values(by="Total Reservations", ascending=False)
    .style.format({
        "Hotel Requests OK": "{:,.0f}",
        "Total Requests": "{:,.0f}",
        "OK": "{:,.0f}",
        "Cancelled": "{:,.0f}",
        "Total Reservations": "{:,.0f}",
        "% Hotel Requests OK": "{:.0%}",
        "Total Cancelled %": "{:.0%}"
    }),
    use_container_width=True
)
