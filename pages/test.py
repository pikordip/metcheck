import numpy as np
import matplotlib.pyplot as plt

# 🎯 Simülasyon Parametreleri
INITIAL_BANKROLL = 5000       # Başlangıç kasası (₺)
WEEKLY_BETS = 5               # Haftalık kupon sayısı
ODDS = 2.40                   # Sabit oran
WEEKS = 8                     # Simülasyon süresi (hafta)
WIN_PROBABILITY = 0.6         # Kupon başına kazanma olasılığı
SIMULATION_RUNS = 10000       # Simülasyon tekrar sayısı

def run_simulation(runs=SIMULATION_RUNS):
    """Bahis stratejisini belirli parametrelerle simüle eder."""
    results = []

    for _ in range(runs):
        bankroll = INITIAL_BANKROLL
        for _ in range(WEEKS):
            per_bet = bankroll / WEEKLY_BETS
            outcomes = np.random.rand(WEEKLY_BETS) < WIN_PROBABILITY
            winnings = np.sum(outcomes) * per_bet * ODDS
            bankroll = winnings  # Sadece kazançlar tekrar yatırılıyor
        results.append(bankroll)

    return results

def summarize_results(results):
    """Simülasyon sonuçlarını istatistiksel olarak özetler."""
    results_array = np.array(results)
    return {
        "Ortalama Son Kasa": np.mean(results_array),
        "Medyan Son Kasa": np.median(results_array),
        "Minimum": np.min(results_array),
        "Maksimum": np.max(results_array),
        "Başarılı (100K üstü)": np.sum(results_array > 100_000),
        "Başarısız (10K altı)": np.sum(results_array < 10_000),
    }

def plot_results(results):
    """Sonuçları histogram olarak görselleştirir."""
    plt.figure(figsize=(10, 6))
    plt.hist(results, bins=50, color="skyblue", edgecolor="black")
    plt.title("8 Haftalık Bahis Simülasyonu Sonuçları")
    plt.xlabel("Son Kasa Tutarı (₺)")
    plt.ylabel("Frekans")
    plt.grid(True)
    plt.axvline(np.mean(results), color='red', linestyle='dashed', linewidth=2,
                label=f"Ortalama: {np.mean(results):,.0f}₺")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    simulated = run_simulation()
    summary = summarize_results(simulated)

    for key, value in summary.items():
        print(f"{key}: {value:,.2f}")

    plot_results(simulated)
