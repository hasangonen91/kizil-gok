# -*- coding: utf-8 -*-
"""Orantılı seyrükleme (proportional navigation) güdümlü füze."""
import math
import numpy as np


class Missile:
    def __init__(self, cfg):
        self.cfg = cfg
        self.pos = np.array(cfg.MISSILE_START, dtype=float)
        self.speed = cfg.MISSILE_SPEED
        tgt = np.array(cfg.TARGET, dtype=float)
        self.heading = math.atan2(tgt[1] - self.pos[1], tgt[0] - self.pos[0])
        self.prev_los = self.heading
        self.lock = 1.0
        self.burnout = False
        self.burn_time = None
        self.bias = 0.0          # seeker yanılsama açısı (rad)

    def _los_angle(self):
        tgt = np.array(self.cfg.TARGET, dtype=float)
        return math.atan2(tgt[1] - self.pos[1], tgt[0] - self.pos[0])

    def step(self, dt, attenuation, rng):
        c = self.cfg
        if not self.burnout:
            los = self._los_angle()
            authority = c.GUIDE_AUTHORITY_FLOOR + \
                (1.0 - c.GUIDE_AUTHORITY_FLOOR) * self.lock
            # körlükte seeker yanlış noktaya kilitlenir: sistematik kayma
            if self.lock < 0.6 and attenuation > 0.2:
                self.bias += rng.normal(0.0, c.SEEKER_BIAS_RATE) * math.sqrt(dt)
            else:
                self.bias *= math.exp(-dt / 1.5)
            measured_los = los + self.bias
            los_rate = math.atan2(math.sin(measured_los - self.prev_los),
                                  math.cos(measured_los - self.prev_los)) / dt
            turn = authority * c.NAV_GAIN * los_rate + \
                rng.normal(0.0, c.SEEKER_NOISE * (1.0 - self.lock) * abs(attenuation))
            self.heading += turn * dt
            self.prev_los = measured_los
            self.lock = min(1.0, self.lock + c.LOCK_RECOVER_RATE * dt *
                            (1.0 - attenuation))

        self.pos = self.pos + self.speed * np.array(
            [math.cos(self.heading), math.sin(self.heading)]) * dt

    def ignite_seeker(self, t):
        self.burnout = True
        self.burn_time = t
