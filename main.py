import streamlit as st

# --- Sayfa Ayarı ---
st.set_page_config(page_title="Ana Sayfa", page_icon="🏠", layout="wide")

# --- Başlık ---
st.title("🏠 Metbeds Kontrol Paneli")

# --- Açıklama ---
st.markdown("""
Hoş geldiniz!  
Bu panel üzerinden operasyonel raporlamalara geçiş yapabilirsiniz.

Sol menüden analiz sayfalarına erişerek sorgu ve rezervasyon verilerini görüntüleyebilirsiniz.
""")
