import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Fatura Kontrol Aracı", layout="wide")
st.title("💼 Döviz Bazlı Grup Fatura Kontrolü")

uploaded_file = st.file_uploader("Excel dosyanızı yükleyin", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Sayısal dönüşüm
    def to_float(val):
        try:
            return float(str(val).replace(".", "").replace(",", "."))
        except:
            return 0.0

    # Türk biçimlendirme
    def format_tr(val):
        try:
            return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return val

    # Durum belirleme (±0.01 tolerans)
    def get_status(fark):
        if abs(fark) < 0.01:
            return "Tam Ödendi"
        elif fark > 0:
            return "Eksik Ödeme"
        else:
            return "Fazla Ödendi"

    status_colors = {
        "Eksik Ödeme": "#FFCCCC",
        "Fazla Ödendi": "#CCFFCC",
        "Tam Ödendi": "#FFFFCC"
    }

    currencies = ["EUR", "GBP", "USD", "TRY"]
    report_rows = []

    for cur in currencies:
        inv_col = f"{cur}|Invoice"
        paid_col = f"{cur}|Rec.Paid"
        if inv_col in df.columns and paid_col in df.columns:
            df["Voucher"] = df["Voucher"].astype(str)
            df[inv_col] = df[inv_col].apply(to_float)
            df[paid_col] = df[paid_col].apply(to_float)

            grouped = df.groupby("Voucher")[[inv_col, paid_col]].sum().reset_index()

            for _, row in grouped.iterrows():
                voucher = row["Voucher"]
                inv = row[inv_col]
                paid = row[paid_col]
                fark = inv - paid
                durum = get_status(fark)

                report_rows.append({
                    "Voucher": voucher,
                    "Döviz Cinsi": cur,
                    "Toplam Invoice": format_tr(inv),
                    "Toplam Rec.Paid": format_tr(paid),
                    "Fark": format_tr(fark),
                    "Durum": durum
                })

    report_df = pd.DataFrame(report_rows)

    # 🔍 Filtreleme
    st.sidebar.header("🔎 Filtrele")
    selected_currency = st.sidebar.multiselect("Döviz Cinsi", report_df["Döviz Cinsi"].unique(), report_df["Döviz Cinsi"].unique())
    selected_status = st.sidebar.multiselect("Durum", report_df["Durum"].unique(), report_df["Durum"].unique())

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

        durum_col_idx = filtered_df.columns.get_loc("Durum")
        for row_num, value in enumerate(filtered_df["Durum"], start=1):
            color = status_colors.get(value, None)
            if color:
                fmt = workbook.add_format({'bg_color': color})
                worksheet.write(row_num, durum_col_idx, value, fmt)

    st.download_button(
        label="📥 Raporu Excel Olarak İndir",
        data=output.getvalue(),
        file_name="grup_kontrol_raporu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
