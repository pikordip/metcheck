import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Fatura Kontrol Aracı", layout="wide")
st.title("💼 Döviz Bazlı Fatura ve Ödeme Kontrolü")

uploaded_file = st.file_uploader("Excel dosyanızı yükleyin", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("📋 Yüklenen Veri")
    st.dataframe(df)

    currencies = ["EUR", "GBP", "USD", "TRY"]
    status_colors = {
        "Eksik Ödeme": "#FFCCCC",   # Kırmızı
        "Fazla Ödendi": "#CCFFCC",  # Yeşil
        "Tam Ödendi": "#FFFFCC"     # Sarı
    }

    # Kontrol sütunlarını ekle
    for cur in currencies:
        invoice_col = f"{cur}|Invoice"
        paid_col = f"{cur}|Rec.Paid"
        status_col = f"{cur}|Status"

        if invoice_col in df.columns and paid_col in df.columns:
            df[status_col] = df[invoice_col] - df[paid_col]

            def get_status(row):
                fark = row[status_col]
                if pd.isna(fark):
                    return ""
                elif fark == 0:
                    return "Tam Ödendi"
                elif fark > 0:
                    return "Eksik Ödeme"
                else:
                    return "Fazla Ödendi"

            df[f"{cur}|Durum"] = df.apply(get_status, axis=1)

    st.subheader("✅ Kontrol Sonuçları")
    st.dataframe(df)

    # Excel çıktısı oluştur
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Kontrol')

        workbook = writer.book
        worksheet = writer.sheets['Kontrol']

        # Durum sütunlarını renklendir
        for idx, col in enumerate(df.columns):
            if col.endswith("|Durum"):
                col_idx = df.columns.get_loc(col)
                for row_num, value in enumerate(df[col], start=1):
                    color = status_colors.get(value, None)
                    if color:
                        worksheet.write(row_num, col_idx, value, workbook.add_format({'bg_color': color}))

    st.download_button(
        label="📥 Düzenlenmiş Excel'i İndir",
        data=output.getvalue(),
        file_name="kontrol_raporu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
