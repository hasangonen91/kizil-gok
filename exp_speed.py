# -*- coding: utf-8 -*-
"""Füze hizi deneyi (hizli surum): bulut her tohum icin BIR KEZ simule edilir,
uc farkli hizda füze ayni buluta karsi kosar. Varis ani sabit tutulur.
Kullanim: python3 exp_speed.py
"""
import numpy as np

from sim import config as C
from sim.particles import ParticleCloud
from sim.missile import Missile
from sim import effects

SEEDS = range(1, 6)
SPEEDS = (300.0, 600.0, 1200.0)
END_T = 12.0

BASE_DISP = [
    {"pos": (-420.0, 165.0), "cone_deg": (166.0, 198.0), "speed": (170.0, 365.0)},
    {"pos": (-900.0, 155.0), "cone_deg": (-18.0, 14.0), "speed": (170.0, 365.0)},
]
LAYERED_DISP = BASE_DISP + [
    {"pos": (-1450.0, 205.0), "cone_deg": (166.0, 198.0), "speed": (170.0, 365.0)},
    {"pos": (-1950.0, 245.0), "cone_deg": (-18.0, 14.0), "speed": (170.0, 365.0)},
]

CONFIGS = {
    "TABAN (900, K=15, q=1)": dict(n=900, k_coul=15.0, q0=1.0, disp=BASE_DISP),
    "YOGUN (1800, K=3.75, q=2)": dict(n=1800, k_coul=3.75, q0=2.0, disp=BASE_DISP),
    "KATMANLI (2x900, K=15, q=2)": dict(n=1800, k_coul=15.0, q0=2.0, disp=LAYERED_DISP),
}


def apply_cfg(p):
    C.N_PARTICLES = p["n"]
    C.COULOMB_K = p["k_coul"]
    C.Q0 = p["q0"]
    C.DISPENSERS = p["disp"]


def run_trial(p, label):
    """Donus: {hiz: (etkisiz, vurdu)} sayaclari."""
    apply_cfg(p)
    counts = {sp: [0, 0] for sp in SPEEDS}
    for seed in SEEDS:
        cfg = C
        cfg.SEED = seed
        cloud = ParticleCloud(cfg)

        missiles = {}
        for idx, sp in enumerate(SPEEDS):
            k = sp / 300.0
            cfg.MISSILE_SPEED = sp
            cfg.MISSILE_START = (-3100.0 * k, 430.0)
            m = Missile(cfg)
            missiles[sp] = {
                "m": m,
                "rng": np.random.default_rng(seed * 100 + idx),
                "done": False,
            }

        steps = int(END_T / cfg.DT)
        for i in range(steps):
            t = i * cfg.DT
            if t < cfg.BULUT_DEPLOY_T:
                continue
            cloud.step(cfg.DT)
            for sp, st in missiles.items():
                if st["done"]:
                    continue
                m = st["m"]
                count = cloud.density_at(m.pos[None, :])[0]
                att = effects.attenuation(count, cfg)
                effects.update_lock(m, att, cfg.DT, cfg)
                effects.burnout_roll(m, count, t, cfg.DT, cfg, st["rng"])
                m.step(cfg.DT, att, st["rng"])
                dist = float(np.linalg.norm(m.pos - np.array(cfg.TARGET)))
                if m.pos[1] <= 0 or dist < cfg.HIT_RADIUS * 0.4:
                    st["done"] = True
                    if dist < cfg.HIT_RADIUS and not m.burnout:
                        counts[sp][1] += 1
                    else:
                        counts[sp][0] += 1
        for sp, st in missiles.items():
            if not st["done"]:
                m = st["m"]
                dist = float(np.linalg.norm(m.pos - np.array(cfg.TARGET)))
                if dist < cfg.HIT_RADIUS and not m.burnout:
                    counts[sp][1] += 1
                else:
                    counts[sp][0] += 1
    return counts


def main():
    print("=" * 64)
    print(f"HIZ DENEYI — {len(SEEDS)} tohum, varis ani sabit (bulut ayni yasta)")
    print("Etkisiz = SAPTI veya dud cakilma | Vurdu = hedefe 22m icinde patlama")
    print("=" * 64, flush=True)
    for name, p in CONFIGS.items():
        print(f"\n--- {name} ---", flush=True)
        counts = run_trial(p, name)
        print(f"{'HIZ':>10} | {'ETKISIZ':>8} | {'VURDU':>6} | basari")
        for sp in SPEEDS:
            e, v = counts[sp]
            pct = 100.0 * e / (e + v)
            print(f"{sp:8.0f} m/s | {e:8d} | {v:6d} | %{pct:.0f}", flush=True)
    print("=" * 64)


if __name__ == "__main__":
    main()
