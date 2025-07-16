import streamlit as st
import pandas as pd

# --- 📁 Dosya Yolu Ayarı ---
excel_path = "data/metbeds/NB_DATA.xlsx"
sheet_ana = "ana_data"
sheet_booking = "Product bookings"

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

    booking_df = booking_df[[
        "JP Code", "Agency", "Product Type", "Status by booking element"
    ]].copy()
    booking_df.columns = ["JPCode", "Agency", "ProductType", "Durum"]
    booking_df["Durum"] = booking_df["Durum"].fillna("Unknown").str.strip().str.lower()
    booking_df["ProductType"] = booking_df["ProductType"].fillna("Unknown").str.strip()
    booking_df["Agency"] = booking_df["Agency"].fillna("Unknown").str.strip()

    rez_list = []
    for _, row in ana_df.iterrows():
        jp = row["JPCode"]
        firma = row["Firma"]
        kategori = row["Kategori"].strip().lower()

        if kategori == "supplier":
            ilgili = booking_df[(booking_df["JPCode"] == jp) & (booking_df["ProductType"] == firma)]
        else:
            ilgili = booking_df[(booking_df["JPCode"] == jp) & (booking_df["Agency"] == firma)]

        ok = (ilgili["Durum"] == "ok").sum()
        cancelled = (ilgili["Durum"] == "cancelled").sum()
        toplam = ok + cancelled
        iptal_orani = round(cancelled / toplam, 4) if toplam else 0
        rez_list.append([ok, cancelled, toplam, iptal_orani])

    ana_df[["Rez_OK", "Rez_Cancelled", "Rez_Toplam", "Toplam_Iptal_Orani"]] = rez_list
    return ana_df

# --- Veri Yükle ---
df = load_data(excel_path, excel_path)

# --- 🎛️ Filtreler
st.sidebar.title("🔍 Filtreler")
kategori_list = sorted(df["Kategori"].dropna().unique())
secili_kategori = st.sidebar.selectbox("Kategori Seçin (zorunlu)", kategori_list)

firma_list = sorted(df[df["Kategori"] == secili_kategori]["Firma"].dropna().unique())
secili_firma = st.sidebar.selectbox("Firma Seç", firma_list)

durumlar = ["Tümü", "Satış Var", "Satış Yok"]
secili_durum = st.sidebar.selectbox("Rezervasyon Durumu", durumlar)

df_filtreli = df[(df["Kategori"] == secili_kategori) & (df["Firma"] == secili_firma)]

gosterilecek = df_filtreli[[
    "Otel", "Sorgu_OK", "Toplam_Sorgu", "Sorgu_OK_Yuzde",
    "Rez_OK", "Rez_Cancelled", "Rez_Toplam", "Toplam_Iptal_Orani"
]].copy()

gosterilecek.columns = [
    "Otel", "Hotel Requests OK", "Total Requests", "% Hotel Requests OK",
    "OK", "Cancelled", "Total Reservations", "Total Cancelled %"
]

gosterilecek = gosterilecek.reset_index(drop=True)

# --- Rezervasyon Durumu Filtresi
if secili_durum == "Satış Var":
    gosterilecek = gosterilecek[gosterilecek["Total Reservations"] > 0]
elif secili_durum == "Satış Yok":
    gosterilecek = gosterilecek[gosterilecek["Total Reservations"] == 0]

# --- Sayısal Biçimlendirme
formatlar = {
    "Hotel Requests OK": "{:,.0f}",
    "Total Requests": "{:,.0f}",
    "OK": "{:,.0f}",
    "Cancelled": "{:,.0f}",
    "Total Reservations": "{:,.0f}",
    "% Hotel Requests OK": "{:.0%}",
    "Total Cancelled %": "{:.0%}"
}
for col in formatlar:
    gosterilecek[col] = pd.to_numeric(gosterilecek[col], errors="coerce")

# --- Başlık
st.title("📊 Sorgu Analiz Raporu")
st.subheader(f"Kategori: {secili_kategori} | Firma: {secili_firma} | Durum: {secili_durum}")

# --- Kutucuklarla Toplamlar
toplamlar = gosterilecek.sum(numeric_only=True)
total_sorgu = toplamlar.get("Total Requests", 0)
total_ok_sorgu = toplamlar.get("Hotel Requests OK", 0)
basari_orani = total_ok_sorgu / total_sorgu if total_sorgu else 0

rez_ok = toplamlar.get("OK", 0)
rez_cancelled = toplamlar.get("Cancelled", 0)
toplam_rez = rez_ok + rez_cancelled
iptal_orani = rez_cancelled / toplam_rez if toplam_rez else 0

ust = st.columns(3)
ust[0].metric("Toplam Sorgu", f"{int(total_sorgu):,}".replace(",", "."))
ust[1].metric("Başarı Oranı", f"{basari_orani:.0%}")
ust[2].metric("Dönüş Yapılan Tutar", f"{int(total_ok_sorgu):,}".replace(",", "."))

alt = st.columns(3)
alt[0].metric("Rezervasyon (OK)", f"{int(rez_ok):,}".replace(",", "."))
alt[1].metric("İptal (Cancelled)", f"{int(rez_cancelled):,}".replace(",", "."))
alt[2].metric("İptal Oranı", f"{iptal_orani:.0%}")

# --- Tablonun Gösterimi
st.markdown("### 📌 Detaylı Otel Performansı")
st.dataframe(
    gosterilecek
    .sort_values(by="Total Requests", ascending=False)
    .style.format(formatlar)
    .hide(axis="index"),
    use_container_width=True
)
