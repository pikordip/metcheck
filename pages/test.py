import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 🎯 Simülasyon Parametreleri
INITIAL_BANKROLL = 5000       # Başlangıç kasası (₺)
WEEKLY_BETS = 5               # Haftalık kupon sayısı
ODDS = 2.40                   # Sabit oran
WEEKS = 8                     # Simülasyon süresi (hafta)
WIN_PROBABILITY = 0.6         # Kupon başına kazanma olasılığı
SIMULATION_RUNS = 10000       # Simülasyon tekrar sayısı

# 🔁 Simülasyon Fonksiyonu
def run_simulation(runs=SIMULATION_RUNS):
    results = []
    for _ in range(runs):
        bankroll = INITIAL_BANKROLL
        for _ in range(WEEKS):
            per_bet = bankroll / WEEKLY_BETS
            outcomes = np.random.rand(WEEKLY_BETS) < WIN_PROBABILITY
            winnings = np.sum(outcomes) * per_bet * ODDS
            bankroll = winnings
        results.append(bankroll)
    return results

# 📊 Özet Fonksiyonu
def summarize_results(results):
    results_array = np.array(results)
    return {
        "Ortalama Son Kasa": np.mean(results_array),
        "Medyan Son Kasa": np.median(results_array),
        "Minimum": np.min(results_array),
        "Maksimum": np.max(results_array),
        "Başarılı (100K üstü)": np.sum(results_array > 100_000),
        "Başarısız (10K altı)": np.sum(results_array < 10_000),
    }

# 📈 Görselleştirme Fonksiyonu
def plot_results(results):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(results, bins=50, color="skyblue", edgecolor="black")
    ax.set_title("8 Haftalık Bahis Simülasyonu Sonuçları")
    ax.set_xlabel("Son Kasa Tutarı (₺)")
    ax.set_ylabel("Frekans")
    ax.grid(True)
    ax.axvline(np.mean(results), color='red', linestyle='dashed', linewidth=2,
               label=f"Ortalama: {np.mean(results):,.0f}₺")
    ax.legend()
    st.pyplot(fig)

# 🚀 Streamlit Arayüzü
st.set_page_config(page_title="Bahis Simülasyonu", layout="centered")
st.title("🎲 Bahis Stratejisi Simülasyonu")
st.write("Bu simülasyon, sabit oranlı ve sabit miktarlı kuponlarla 8 haftalık bir stratejinin olası sonuçlarını gösterir.")

# Simülasyonu çalıştır
simulated = run_simulation()
summary = summarize_results(simulated)

# Sonuçları göster
st.subheader("📌 İstatistiksel Özet")
for key, value in summary.items():
    st.write(f"**{key}**: {value:,.2f}₺")

# Histogram çiz
st.subheader("📊 Sonuçların Dağılımı")
plot_results(simulated)
