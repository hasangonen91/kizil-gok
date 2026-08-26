# -*- coding: utf-8 -*-
"""Ana simülasyon döngüsü."""
import math
from typing import Optional
import numpy as np

from .particles import ParticleCloud
from .missile import Missile
from . import effects


class Result:
    def __init__(self):
        self.t = []                    # type: list[float]
        self.missile_pos = []          # type: list[np.ndarray]
        self.missile_heading = []      # type: list[float]
        self.lock = []                 # type: list[float]
        self.att = []                  # type: list[float]
        self.cloud_pos = []            # type: list[np.ndarray]
        self.cloud_q = []              # type: list[np.ndarray]
        self.integrity = []            # type: list[float]
        self.burnout_frame = None      # type: Optional[int]
        self.outcome = "BELIRSIZ"
        self.min_dist = float("inf")
        self.final_dist = 0.0
        self.in_cloud_time = 0.0
        self.max_att = 0.0
        self.missile_burnout = False
        self.burn_time = None          # type: Optional[float]
        self.fuze_dead = False


def run(cfg, deploy_t=None):
    deploy_t = cfg.BULUT_DEPLOY_T if deploy_t is None else deploy_t
    rng = np.random.default_rng(cfg.SEED + 7)
    cloud = ParticleCloud(cfg)
    missile = Missile(cfg)

    res = Result()
    res.t = []
    res.missile_pos = []
    res.missile_heading = []
    res.lock = []
    res.att = []
    res.cloud_pos = []
    res.cloud_q = []
    res.integrity = []
    res.burnout_frame = None

    deployed = False
    in_cloud_time = 0.0
    max_att = 0.0
    min_dist = float("inf")
    outcome = "BELIRSIZ"

    steps = int(cfg.SIM_TIME / cfg.DT)
    for i in range(steps):
        t = i * cfg.DT
        if t >= deploy_t and not deployed:
            deployed = True  # parçacıklar fırlatıldı (cloud zaten kurulu, aktif oluyor)

        if not deployed:
            res.t.append(t)
            res.missile_pos.append(missile.pos.copy())
            res.missile_heading.append(missile.heading)
            res.lock.append(missile.lock)
            res.att.append(0.0)
            res.cloud_pos.append(np.full((cfg.N_PARTICLES, 2), np.nan))
            res.cloud_q.append(np.zeros(cfg.N_PARTICLES))
            res.integrity.append(0.0)
            continue

        cloud.step(cfg.DT)
        count = cloud.density_at(missile.pos[None, :])[0]
        att = effects.attenuation(count, cfg)
        effects.update_lock(missile, att, cfg.DT, cfg)
        if effects.burnout_roll(missile, count, t, cfg.DT, cfg, rng):
            res.burnout_frame = len(res.t)
            res.fuze_dead = rng.random() < cfg.FUZE_SAFE_P_BURNOUT

        missile.step(cfg.DT, att, rng)

        dist = float(np.linalg.norm(missile.pos - np.array(cfg.TARGET)))
        min_dist = min(min_dist, dist)
        if att > 0.15:
            in_cloud_time += cfg.DT
        max_att = max(max_att, att)

        if missile.burnout and dist < cfg.HIT_RADIUS:
            pass  # yanmış seeker, balistik geçiş — vurmadı sayılır

        res.t.append(t + cfg.DT)
        res.missile_pos.append(missile.pos.copy())
        res.missile_heading.append(missile.heading)
        res.lock.append(missile.lock)
        res.att.append(att)
        res.cloud_pos.append(cloud.pos.copy())
        res.cloud_q.append(cloud.q.copy())
        res.integrity.append(cloud.integrity())

        if missile.pos[1] <= 0 or dist < cfg.HIT_RADIUS * 0.4:
            break

    final = np.linalg.norm(res.missile_pos[-1] - np.array(cfg.TARGET))
    if missile.burnout:
        if res.fuze_dead:
            outcome = "ÇAKILDI — SAVAŞ BAŞLIĞI ETKİSİZ (dud, patlamadı)"
        else:
            outcome = "ÇAKILDI — PATLAMA (S&A devresi hayatta kaldı)"
    elif min_dist < cfg.HIT_RADIUS:
        outcome = "VURDU — bulut yetersiz"
    else:
        outcome = "SAPTI — bulut füzeyi kör etti"

    res.outcome = outcome
    res.min_dist = min_dist
    res.final_dist = float(final)
    res.in_cloud_time = in_cloud_time
    res.max_att = max_att
    res.missile_burnout = missile.burnout
    res.burn_time = missile.burn_time
    return res
