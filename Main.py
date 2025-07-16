import streamlit as st

# --- Sayfa Ayarları ---
st.set_page_config(page_title="Ana Sayfa", page_icon="🏠", layout="wide")

# --- Başlık ---
st.title("🏠 Metbeds Dashboard Ana Sayfa")
st.markdown("Merhaba 👋 Bu panel üzerinden sorgu ve rezervasyon analiz sayfalarına erişebilir, operasyon verilerinizi dinamik biçimde görüntüleyebilirsiniz.")

# --- Sayfaya Giriş Kutuları ---
st.markdown("### 📂 Sayfa Seçimi")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🔎 Sorgu Analiz Raporu")
    st.info("Sorguların otel bazlı başarım oranları, rezervasyon dönüş analizleri ve ajans/supplier filtreleriyle detaylı inceleme.")
    if st.button("Raporu Aç", key="sorgu_buton"):
        st.switch_page("pages/Sorgu_Analiz_Raporu.py")

with col2:
    st.markdown("#### 📊 Diğer Raporlar (Gelecek)")
    st.warning("Yeni rapor sayfaları eklendikçe buradan erişebileceksiniz.")

# --- İsteğe Bağlı Özet Metrikler (Varsa) ---
st.markdown("---")
st.markdown("### 📌 Kısa Bilgiler")
col3, col4, col5 = st.columns(3)
col3.metric("Toplam Ajans", "12")
col4.metric("İncelenen Otel", "280")
col5.metric("Bugünkü Sorgu", "1.284")

# --- Footer ---
st.markdown("---")
st.caption("📅 Son güncelleme: 16 Temmuz 2025 — Hazırlayan: Metin + Copilot")

