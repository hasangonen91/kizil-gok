# -*- coding: utf-8 -*-
"""Headless simülasyon çalıştırıcı: sonuç özetini yazdırır.
Kullanım: python3 run_sim.py [seed]
"""
import sys
from sim import config as C
from sim.engine import run


def main():
    if len(sys.argv) > 1:
        C.SEED = int(sys.argv[1])
    res = run(C)
    print("=" * 52)
    print("BULUT-KALKAN v0.1 — Elektron Bulut Aktif Koruma Simülatörü")
    print("=" * 52)
    print(f"Tohum (seed)          : {C.SEED}")
    print(f"Füze başlangıç        : {C.MISSILE_START}  hız {C.MISSILE_SPEED:.0f} m/s")
    print(f"Bulut fırlatma        : t={C.BULUT_DEPLOY_T}s  parçacık={C.N_PARTICLES}")
    print(f"RF bakım ışını        : {'AÇIK (tau=%ds)' % C.RF_BEAM_TAU if C.RF_BEAM else 'KAPALI'}")
    print("-" * 52)
    print(f"SONUÇ                 : {res.outcome}")
    print(f"Hedefe min. mesafe    : {res.min_dist:.0f} m")
    print(f"Son mesafe            : {res.final_dist:.0f} m")
    print(f"Bulutta kalma süresi  : {res.in_cloud_time:.2f} s")
    print(f"Maks. sinyal zayıflama: %{res.max_att * 100:.0f}")
    if res.missile_burnout:
        print(f"Seeker yanma anı      : t={res.burn_time:.2f} s")
        print(f"Savaş başlığı         : {'ETKİSİZ (dud)' if res.fuze_dead else 'PATLADI'}")
    print(f"Simülasyon süresi     : {res.t[-1]:.2f} s")
    print("=" * 52)


if __name__ == "__main__":
    main()
