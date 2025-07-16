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

    ana_df = ana_df[[
        "Hotel", "JPCode", "Hotel Requests OK", "% Hotel Requests OK",
        "Total Hotel Requests", "Kategori", "SEÇ"
    ]].copy()
    ana_df.columns = [
        "Otel", "JPCode", "Sorgu_OK", "Yuzdelik_Sorgu_OK", "Toplam_Sorgu",
        "Kategori", "Firma"
    ]

    ana_df["Sorgu_OK_Yuzde"] = (
        ana_df["Sorgu_OK"] / ana_df["Toplam_Sorgu"]
    ).fillna(0).round(4)

    booking_df = booking_df[["JP Code", "Agency", "Status by booking element"]].copy()
    booking_df.columns = ["JPCode", "Agency", "Durum"]
    booking_df["Durum"] = booking_df["Durum"].fillna("Unknown").str.strip().str.lower()

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

# --- 🎛️ Sidebar Filtreler ---
st.sidebar.title("🔍 Filtreler")

kategori_list = sorted(df["Kategori"].dropna().unique())
secili_kategori = st.sidebar.selectbox("Kategori Seçin (zorunlu)", kategori_list)

firma_list = sorted(df[df["Kategori"] == secili_kategori]["Firma"].dropna().unique())
secili_firma = st.sidebar.selectbox("Firma Seç", firma_list)

rezervasyon_durumlari = ["Tümü", "Satış Var", "Satış Yok"]
secili_durum = st.sidebar.selectbox("Rezervasyon Durumu", rezervasyon_durumlari)

df_filtreli = df[(df["Kategori"] == secili_kategori) & (df["Firma"] == secili_firma)]

# --- 📋 Gösterilecek Alanlar ---
gosterilecek = df_filtreli[[
    "Otel", "Sorgu_OK", "Toplam_Sorgu", "Sorgu_OK_Yuzde",
    "Rez_OK", "Rez_Cancelled", "Rez_Toplam", "Toplam_Iptal_Orani"
]].copy()

gosterilecek.columns = [
    "Otel", "Hotel Requests OK", "Total Requests", "% Hotel Requests OK",
    "OK", "Cancelled", "Total Reservations", "Total Cancelled %"
]

gosterilecek = gosterilecek.reset_index(drop=True)

if secili_durum == "Satış Var":
    gosterilecek = gosterilecek[gosterilecek["OK"] > 0]
elif secili_durum == "Satış Yok":
    gosterilecek = gosterilecek[gosterilecek["OK"] == 0]

sayisal_formatlar = {
    "Hotel Requests OK": "{:,.0f}",
    "Total Requests": "{:,.0f}",
    "OK": "{:,.0f}",
    "Cancelled": "{:,.0f}",
    "Total Reservations": "{:,.0f}",
    "% Hotel Requests OK": "{:.0%}",
    "Total Cancelled %": "{:.0%}"
}

for col in sayisal_formatlar:
    gosterilecek[col] = pd.to_numeric(gosterilecek[col], errors="coerce")

# --- 📄 Sayfa Başlığı ---
st.title("📊 Sorgu Analiz Raporu")
st.subheader(f"Kategori: {secili_kategori} | Firma: {secili_firma} | Durum: {secili_durum}")

# --- 📦 Metrikler: Toplamlar Kutucuklarında
toplamlar = gosterilecek.sum(numeric_only=True)
kareler = st.columns(6)
metric_labels = [
    ("Total Requests", "Total Requests"),
    ("Hotel Requests OK", "Hotel Requests OK"),
    ("OK", "OK"),
    ("Cancelled", "Cancelled"),
    ("Total Reservations", "Total Reservations"),
    ("Total Cancelled %", "Total Cancelled %")
]
for i, (etiket, kolon) in enumerate(metric_labels):
    deger = toplamlar.get(kolon, 0)
    if "Yuzde" in kolon or "%" in kolon:
        kareler[i].metric(etiket, f"{deger:.0%}")
    else:
        kareler[i].metric(etiket, f"{int(deger):,}".replace(",", "."))

# --- 📊 Tablo Gösterimi ---
st.markdown("### 📌 Detaylı Otel Performansı")
st.dataframe(
    gosterilecek
    .sort_values(by="Total Requests", ascending=False)
    .style.format(sayisal_formatlar)
    .hide(axis="index"),
    use_container_width=True
)
