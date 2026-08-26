# -*- coding: utf-8 -*-
"""Plazma elektrot yerleşim optimizasyonu — Genetik Algoritma.

Amaç: Füze savunma başarı oranını maksimize edecek elektrot konumlarını bulmak.
"""
import random
import sys
import os
import numpy as np
from copy import deepcopy

# sim modülünü import et
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import config as base_cfg
from sim.engine import run


class SimConfig:
    """Simülasyon parametrelerini tutan basit obje."""
    def __init__(self):
        # base_cfg'den tüm değerleri kopyala
        for attr in dir(base_cfg):
            if not attr.startswith('_'):
                setattr(self, attr, getattr(base_cfg, attr))


def make_config(electrodes, seed=42):
    """Verilen elektrotlarla yeni config oluştur."""
    cfg = SimConfig()
    cfg.SEED = seed
    cfg.PLASMA_ELECTRODES = electrodes
    cfg.PLASMA_MODE = True
    return cfg


# ---- GA Parametreleri ----
POP_SIZE = 30           # Popülasyon büyüklüğü
N_GENERATIONS = 25      # Nesil sayısı
N_ELECTRODES = 6        # Elektrot sayısı
N_TEST_SEEDS = 8        # Her birey için test edilecek tohum sayısı
MUTATION_RATE = 0.3     # Mutasyon olasılığı
MUTATION_SIGMA = 80.0   # Mutasyon_std dev (metre)
CROSSOVER_RATE = 0.7    # Çaprazlama olasılığı

# Arama alanı (elektrot konumları için)
X_MIN, X_MAX = -2000.0, 100.0    # Füze geliş yönü boyunca
Y_MIN, Y_MAX = 50.0, 600.0       # Dikey (yerden yükseklik)


def random_electrode():
    """Rastgele bir elektrot konumu üret."""
    return (random.uniform(X_MIN, X_MAX), random.uniform(Y_MIN, Y_MAX))


def random_individual():
    """Rastgele bir birey (elektrot yerleşimi) üret."""
    return [random_electrode() for _ in range(N_ELECTRODES)]


def fitness(individual, test_seeds=None):
    """Bireyin fitness değeri — başarı oranı + ortalama sapma mesafesi.

    Returns:
        float: fitness skoru (0-100 arası, yüksek = iyi)
    """
    if test_seeds is None:
        test_seeds = list(range(1, N_TEST_SEEDS + 1))

    wins = 0
    total_deflection = 0.0

    for seed in test_seeds:
        cfg = make_config(individual, seed)
        try:
            res = run(cfg)
            if 'SAPTI' in res.outcome or 'ÇAKILDI' in res.outcome:
                wins += 1
                total_deflection += res.min_dist
            else:
                # VURDU — negatif skor (yakınlık kadar ceza)
                total_deflection -= max(0, base_cfg.HIT_RADIUS - res.min_dist)
        except Exception:
            pass  # Hata olursa bu tohumu atla

    success_rate = wins / len(test_seeds)
    avg_deflection = total_deflection / len(test_seeds)

    # Fitness: %60 başarı + %40 ortalama sapma
    fitness_score = success_rate * 60 + min(40, avg_deflection / 50)
    return fitness_score


def crossover(parent1, parent2):
    """Çaprazlama: iki ebeveynin elektrotlarını karıştır."""
    child = []
    for i in range(N_ELECTRODES):
        if random.random() < 0.5:
            child.append(parent1[i])
        else:
            child.append(parent2[i])
    return child


def mutate(individual):
    """Mutasyon: elektrot konumlarını rastgele kaydır."""
    mutated = []
    for x, y in individual:
        if random.random() < MUTATION_RATE:
            x += random.gauss(0, MUTATION_SIGMA)
            y += random.gauss(0, MUTATION_SIGMA * 0.5)
            # Sınırlar içinde tut
            x = max(X_MIN, min(X_MAX, x))
            y = max(Y_MIN, min(Y_MAX, y))
        mutated.append((x, y))
    return mutated


def tournament_select(population, fitnesses, k=3):
    """Turnuva seçimi: rastgele k bireyden en iyisini seç."""
    indices = random.sample(range(len(population)), k)
    best = max(indices, key=lambda i: fitnesses[i])
    return population[best]


def run_ga():
    """Genetik algoritmayı çalıştır."""
    print("=" * 60)
    print("GENETİK ALGORİTMA — PLAZMA ELEKTROT YERLEŞİM OPTİMİZASYONU")
    print("=" * 60)
    print(f"Popülasyon: {POP_SIZE} | Nesil: {N_GENERATIONS} | Elektrot: {N_ELECTRODES}")
    print(f"Test tohumu: {N_TEST_SEEDS} | Mutasyon: %{MUTATION_RATE*100}")
    print("-" * 60)

    # Başlangıç popülasyonu
    population = [random_individual() for _ in range(POP_SIZE)]

    best_ever = None
    best_ever_fitness = -1

    for gen in range(N_GENERATIONS):
        # Fitness hesapla
        fitnesses = [fitness(ind) for ind in population]

        # En iyiyi bul
        gen_best_idx = np.argmax(fitnesses)
        gen_best_fitness = fitnesses[gen_best_idx]
        gen_best = population[gen_best_idx]

        if gen_best_fitness > best_ever_fitness:
            best_ever_fitness = gen_best_fitness
            best_ever = deepcopy(gen_best)

        # İstatistikler
        avg_fit = np.mean(fitnesses)
        print(f"Nesil {gen+1:2d}/{N_GENERATIONS} | "
              f"En İyi: {gen_best_fitness:.1f} | "
              f"Ortalama: {avg_fit:.1f} | "
              f"Rekor: {best_ever_fitness:.1f}")

        # Yeni popülasyon oluştur
        new_population = [deepcopy(gen_best)]  # Elitizm: en iyiyi koru

        while len(new_population) < POP_SIZE:
            p1 = tournament_select(population, fitnesses)
            p2 = tournament_select(population, fitnesses)

            if random.random() < CROSSOVER_RATE:
                child = crossover(p1, p2)
            else:
                child = deepcopy(p1)

            child = mutate(child)
            new_population.append(child)

        population = new_population

    # Sonuçları göster
    print("\n" + "=" * 60)
    print("OPTİMİZASYON TAMAMLANDI — EN İYİ YERLEŞİM")
    print("=" * 60)
    print(f"Fitness: {best_ever_fitness:.1f}/100")
    print(f"\nElektrot Konumları:")
    for i, (x, y) in enumerate(best_ever):
        print(f"  {i+1}. ({x:.0f}, {y:.0f}) m")

    # Detaylı test
    print(f"\nDetaylı test ({N_TEST_SEEDS * 3} tohum):")
    test_seeds = list(range(1, N_TEST_SEEDS * 3 + 1))
    wins = 0
    for seed in test_seeds:
        cfg = make_config(best_ever, seed)
        try:
            res = run(cfg)
            status = "✓" if ('SAPTI' in res.outcome or 'ÇAKILDI' in res.outcome) else "✗"
            print(f"  Tohum {seed:2d}: {status} {res.outcome[:35]:35s} min:{res.min_dist:.0f}m")
            if 'SAPTI' in res.outcome or 'ÇAKILDI' in res.outcome:
                wins += 1
        except Exception as e:
            print(f"  Tohum {seed:2d}: HATA — {e}")

    print(f"\n{'=' * 60}")
    print(f"BAŞARI ORANI: {wins}/{len(test_seeds)} = %{wins*100/len(test_seeds):.0f}")
    print(f"{'=' * 60}")

    return best_ever, best_ever_fitness


if __name__ == "__main__":
    best_placement, best_score = run_ga()
