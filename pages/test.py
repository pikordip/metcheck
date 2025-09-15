import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Fatura Kontrol Aracı", layout="wide")
st.title("💼 Döviz Bazlı Fatura ve Ödeme Kontrolü")

uploaded_file = st.file_uploader("Excel dosyanızı yükleyin", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Sayısal sütunları Türk formatına uygun şekilde temizle
    def clean_numeric(col):
        return pd.to_numeric(
            df[col].astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False),
            errors="coerce"
        )

    # Sayıyı Türk noktalama sistemine göre biçimlendir
    def format_turkish_number(val):
        try:
            return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return val

    # Durum belirleme
    def get_status(val):
        if pd.isna(val):
            return ""
        elif val == 0:
            return "Tam Ödendi"
        elif val > 0:
            return "Eksik Ödeme"
        else:
            return "Fazla Ödendi"

    # Renk kodları
    status_colors = {
        "Eksik Ödeme": "#FFCCCC",   # Kırmızı
        "Fazla Ödendi": "#CCFFCC",  # Yeşil
        "Tam Ödendi": "#FFFFCC"     # Sarı
    }

    # Rapor tablosu oluştur
    report_rows = []
    currencies = ["EUR", "GBP", "USD", "TRY"]

    for idx, row in df.iterrows():
        voucher = row.get("Voucher", "")
        for cur in currencies:
            invoice_col = f"{cur}|Invoice"
            paid_col = f"{cur}|Rec.Paid"

            if invoice_col in df.columns and paid_col in df.columns:
                invoice = row[invoice_col]
                paid = row[paid_col]

                try:
                    invoice_clean = float(str(invoice).replace(".", "").replace(",", "."))
                    paid_clean = float(str(paid).replace(".", "").replace(",", "."))
                except:
                    invoice_clean = 0.0
                    paid_clean = 0.0

                fark = invoice_clean - paid_clean
                durum = get_status(fark)
                fark_formatted = format_turkish_number(fark)

                report_rows.append({
                    "Voucher": voucher,
                    "Döviz Cinsi": cur,
                    "Invoice Tutarı": format_turkish_number(invoice_clean),
                    "Rec.Paid Tutarı": format_turkish_number(paid_clean),
                    "Fark": fark_formatted,
                    "Durum": durum
                })

    report_df = pd.DataFrame(report_rows)
    st.subheader("✅ Kontrol Raporu")
    st.dataframe(report_df)

    # Excel çıktısı oluştur
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name='Rapor')
        workbook = writer.book
        worksheet = writer.sheets['Rapor']

        # Durum sütununu renklendir
        durum_col_idx = report_df.columns.get_loc("Durum")
        for row_num, value in enumerate(report_df["Durum"], start=1):
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
