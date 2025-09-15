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

    currencies = ["EUR", "GBP", "USD", "TRY"]
    status_colors = {
        "Eksik Ödeme": "#FFCCCC",   # Kırmızı
        "Fazla Ödendi": "#CCFFCC",  # Yeşil
        "Tam Ödendi": "#FFFFCC"     # Sarı
    }

    for cur in currencies:
        invoice_col = f"{cur}|Invoice"
        paid_col = f"{cur}|Rec.Paid"
        status_col = f"{cur}|Fark"
        durum_col = f"{cur}|Durum"

        if invoice_col in df.columns and paid_col in df.columns:
            df[invoice_col] = clean_numeric(invoice_col)
            df[paid_col] = clean_numeric(paid_col)

            df[status_col] = df[invoice_col].fillna(0) - df[paid_col].fillna(0)

            def get_status(val):
                if pd.isna(val):
                    return ""
                elif val == 0:
                    return "Tam Ödendi"
                elif val > 0:
                    return "Eksik Ödeme"
                else:
                    return "Fazla Ödendi"

            df[durum_col] = df[status_col].apply(get_status)

            # Görsel için biçimlendirilmiş sayı sütunu ekle
            df[f"{cur}|Fark (Görsel)"] = df[status_col].apply(format_turkish_number)

    st.subheader("✅ Kontrol Sonuçları")
    st.dataframe(df)

    # Excel çıktısı oluştur
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Kontrol')
        workbook = writer.book
        worksheet = writer.sheets['Kontrol']

        # Renklendirme
        for col in df.columns:
            if col.endswith("|Durum"):
                col_idx = df.columns.get_loc(col)
                for row_num, value in enumerate(df[col], start=1):
                    color = status_colors.get(value, None)
                    if color:
                        fmt = workbook.add_format({'bg_color': color})
                        worksheet.write(row_num, col_idx, value, fmt)

    st.download_button(
        label="📥 Düzenlenmiş Excel'i İndir",
        data=output.getvalue(),
        file_name="kontrol_raporu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
