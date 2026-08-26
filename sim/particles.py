# -*- coding: utf-8 -*-
"""Yüklü parçacık bulutu dinamiği."""
import numpy as np


class ParticleCloud:
    def __init__(self, cfg):
        rng = np.random.default_rng(cfg.SEED)
        self.cfg = cfg
        n_total = cfg.N_PARTICLES

        pos_list, vel_list, q_list = [], [], []
        share = n_total // len(cfg.DISPENSERS)
        counts = [share] * len(cfg.DISPENSERS)
        counts[0] += n_total - sum(counts)

        for d_cfg, n in zip(cfg.DISPENSERS, counts):
            ang = np.deg2rad(rng.uniform(d_cfg["cone_deg"][0], d_cfg["cone_deg"][1], n))
            spd = rng.uniform(d_cfg["speed"][0], d_cfg["speed"][1], n)

            p = np.empty((n, 2))
            p[:, 0] = d_cfg["pos"][0] + rng.uniform(-8, 8, n)
            p[:, 1] = d_cfg["pos"][1] + rng.uniform(-4, 4, n)

            v = np.empty((n, 2))
            v[:, 0] = spd * np.cos(ang)
            v[:, 1] = spd * np.sin(ang)

            q_sign = np.where(rng.random(n) < cfg.CHARGE_MIX, 1.0, -1.0)

            pos_list.append(p)
            vel_list.append(v)
            q_list.append(q_sign * cfg.Q0)

        self.pos = np.vstack(pos_list)
        self.vel = np.vstack(vel_list)
        self.q = np.concatenate(q_list)
        self.total_q0 = float(np.abs(self.q).sum())

    def step(self, dt):
        c = self.cfg
        d = self.pos[None, :, :] - self.pos[:, None, :]
        r2 = (d * d).sum(-1)
        np.fill_diagonal(r2, np.inf)
        r2 = r2 + c.SOFTENING ** 2
        qq = self.q[None, :, None] * self.q[:, None, None]
        # itme: aynı işaretse kuvvet, i'den j'ye doğru DEĞİL, tersi olmalı
        F = -(c.COULOMB_K * qq * d / r2[..., None]).sum(axis=1)

        acc = F.copy()
        acc[:, 1] -= c.GRAVITY
        acc -= c.DRAG * self.vel

        self.vel += acc * dt
        self.pos += self.vel * dt
        tau = c.RF_BEAM_TAU if getattr(c, "RF_BEAM", False) else c.CHARGE_DECAY_TAU
        self.q *= np.exp(-dt / tau)

    def integrity(self):
        return float(np.abs(self.q).sum()) / self.total_q0

    def density_at(self, points):
        """Nokta çevresindeki (yarıçap içindeki) mutlak yüklü parçacık sayısı."""
        c = self.cfg
        alive = np.abs(self.q) > 0.02
        if not alive.any():
            return np.zeros(len(points))
        w = np.abs(self.q)[alive][:, None]
        diff = points[None, :, :] - self.pos[alive][:, None, :]
        dist2 = (diff * diff).sum(-1)
        return (w * (dist2 < c.DENSITY_RADIUS ** 2)).sum(axis=0)
