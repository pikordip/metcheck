import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Fatura Kontrol Aracı", layout="wide")
st.title("💼 Döviz Bazlı Fatura ve Ödeme Kontrolü")

uploaded_file = st.file_uploader("Excel dosyanızı yükleyin", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Sayısal dönüşüm ve Türk noktalama biçimi
    def to_float(val):
        try:
            return float(str(val).replace(".", "").replace(",", "."))
        except:
            return 0.0

    def format_tr(val):
        try:
            return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return val

    def get_status(fark):
        if fark == 0:
            return "Tam Ödendi"
        elif fark > 0:
            return "Eksik Ödeme"
        else:
            return "Fazla Ödendi"

    status_colors = {
        "Eksik Ödeme": "#FFCCCC",   # Kırmızı
        "Fazla Ödendi": "#CCFFCC",  # Yeşil
        "Tam Ödendi": "#FFFFCC"     # Sarı
    }

    currencies = ["EUR", "GBP", "USD", "TRY"]
    report_rows = []

    for _, row in df.iterrows():
        voucher = row.get("Voucher", "")
        for cur in currencies:
            inv_col = f"{cur}|Invoice"
            paid_col = f"{cur}|Rec.Paid"
            if inv_col in df.columns and paid_col in df.columns:
                inv = to_float(row[inv_col])
                paid = to_float(row[paid_col])
                fark = inv - paid
                durum = get_status(fark)
                report_rows.append({
                    "Voucher": voucher,
                    "Döviz Cinsi": cur,
                    "Invoice Tutarı": format_tr(inv),
                    "Rec.Paid Tutarı": format_tr(paid),
                    "Fark": format_tr(fark),
                    "Durum": durum
                })

    report_df = pd.DataFrame(report_rows)

    # 🔍 Filtreleme
    st.sidebar.header("🔎 Filtrele")
    selected_currency = st.sidebar.multiselect("Döviz Cinsi", options=report_df["Döviz Cinsi"].unique(), default=report_df["Döviz Cinsi"].unique())
    selected_status = st.sidebar.multiselect("Durum", options=report_df["Durum"].unique(), default=report_df["Durum"].unique())

    filtered_df = report_df[
        report_df["Döviz Cinsi"].isin(selected_currency) &
        report_df["Durum"].isin(selected_status)
    ]

    st.subheader("📊 Kontrol Raporu")
    st.dataframe(filtered_df)

    # 📥 Excel çıktısı
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Rapor')
        workbook = writer.book
        worksheet = writer.sheets['Rapor']

        # Renklendirme
        durum_col_idx = filtered_df.columns.get_loc("Durum")
        for row_num, value in enumerate(filtered_df["Durum"], start=1):
            color = status_colors.get(value, None)
            if color:
                fmt = workbook.add_format({'bg_color': color})
                worksheet.write(row_num, durum_col_idx, value, fmt)

    st.download_button(
        label="📥 Raporu Excel Olarak İndir",
        data=output.getvalue(),
        file_name="kontrol_raporu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
