import streamlit as st

# --- Sayfa Ayarı ---
st.set_page_config(page_title="METCHECK Kontrol Paneli", page_icon="✅", layout="wide")

# --- Başlık ---
st.title("✅ METCHECK Kontrol Paneli")

# --- Açıklama ---
st.markdown("""
Merhaba 👋  
METCHECK'e hoş geldiniz.

Bu panel üzerinden operasyonel kontrolleri, finansal raporlamaları ve rezervasyon analizlerini görüntüleyebilirsiniz.  
Sol menüden ilgili modüllere geçiş yaparak detaylı sorgulama ve veri kontrolü gerçekleştirebilirsiniz.
""")
