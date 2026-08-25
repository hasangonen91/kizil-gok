# -*- coding: utf-8 -*-
"""Bulutun füze arayıcısı (seeker) üzerindeki etkileri."""
import numpy as np


def attenuation(count, cfg):
    """Yerel yüklü parçacık sayısından RF sinyal zayıflaması [0,1]."""
    return float(np.clip(count / cfg.DENS_FULL, 0.0, 0.995))


def update_lock(missile, att, dt, cfg):
    """Kilit kalitesi dinamigi: bulutta erime, temiz havada toparlanma."""
    if missile.burnout:
        missile.lock = 0.0
        return
    if att > 0.05:
        missile.lock -= cfg.LOCK_LOSS_RATE * att * dt
    missile.lock = max(0.0, missile.lock)


def burnout_roll(missile, count, t, dt, cfg, rng):
    """Induksiyon akimiyla seeker yanma olasiligi."""
    if missile.burnout or count < cfg.BURN_COUNT_MIN:
        return False
    excess = (count - cfg.BURN_COUNT_MIN) / cfg.BURN_COUNT_MIN
    p = min(0.9, cfg.BURN_K * excess ** 1.5) * dt
    if rng.random() < p:
        missile.ignite_seeker(t)
        return True
    return False
