# -*- coding: utf-8 -*-
"""Plazma bulutu modeli — aerosol yerine elektriksel iyonizasyon.

Plazma frekansı (ω_p) > radar frekansı (ω_r) olduğunda RF absorbe/rekle edilir.
Elektriksel iyonizasyon ile sürekli plazma üretilir — tüketim malzemesi yoktur.
"""
import math
import numpy as np
from numpy.typing import NDArray


class PlasmaRegion:
    """Yüksek gerilim elektrotları tarafından üretilen plazma bölgesi.

    Araç üzerine monte edilmiş N adet elektrot, aralarındaki havayı iyonize
    ederek plazma bulutu oluşturur. Plazma yoğunluğu elektrot merkezlerinden
    uzaklaştıkça Gaussian olarak azalır.
    """

    def __init__(self, cfg):
        self.cfg = cfg
        self.electrodes = np.array(cfg.PLASMA_ELECTRODES, dtype=float)  # (N, 2)
        self.n_electrodes = len(self.electrodes)
        self.voltage = cfg.PLASMA_VOLTAGE  # kV
        self.gas_density = cfg.PLASMA_GAS_DENSITY  # normalize gaz yoğunluğu

        # Plazma parametreleri (hesaplanan)
        self.peak_density = self._calc_peak_density()
        self.plasma_radius = cfg.PLASMA_RADIUS  # elektrik alan etki yarıçapı (m)

        # Durum: plazma aktif mi?
        self.active = False
        self.activation_time = None

        # Plazma yoğunluğu haritası (elektrot bazlı Gaussian)
        self.n_electrodes_active = self.n_electrodes

    def _calc_peak_density(self):
        """Elektriksel iyonizasyon ile tepe elektron yoğunluğu (m⁻³).

        Değerler corsora deşarj literatürüne dayalı:
        - 30 kV: ~10^14 m⁻³ (düşük)
        - 50 kV: ~10^15 m⁻³ (orta)
        - 100 kV: ~10^16 m⁻³ (yüksek)

        Gerçek değer gaz türüne, elektrot geometrisine ve basıncına bağlıdır.
        """
        # Basit model: n_e ∝ V^1.5 (Peek yasası yaklaşımı)
        v_kv = self.voltage
        # Normalize: 50 kV → 10^15 m⁻³
        n_50kv = 1e15
        n_e = n_50kv * (v_kv / 50.0) ** 1.5
        return n_e

    def _plasma_frequency(self, n_e):
        """Plazma frekansı ω_p (rad/s).

        ω_p = sqrt(n_e * e² / (ε_0 * m_e))
        """
        e = 1.602e-19  # C
        eps_0 = 8.854e-12  # F/m
        m_e = 9.109e-31  # kg
        return math.sqrt(n_e * e ** 2 / (eps_0 * m_e))

    def _rf_attenuation_from_plasma(self, n_e, thickness, freq_hz):
        """Plazmanın RF sinyaline yaptığı zayıflama (dB).

        Basitleştirilmiş model:
        - ω_p < ω_r: zayıf absorpsiyon (underdense)
        - ω_p > ω_r: güçlü absorpsiyon/reklection (overdense)
        - Kalınlık arttıkça zayıflama artar (Beer-Lambert benzeri)
        """
        omega_p = self._plasma_frequency(n_e)
        omega_r = 2 * math.pi * freq_hz
        nu = self.cfg.PLASMA_COLLISION_FREQ  # çarpışma frekansı (Hz)

        # Plazma dielektrik sabiti (basitleştirilmiş)
        # ε_r = 1 - ω_p² / (ω_r² + ν²)
        denom = omega_r ** 2 + nu ** 2
        if denom < 1e-10:
            return 0.0
        eps_r_real = 1.0 - omega_p ** 2 / denom
        eps_r_imag = omega_p ** 2 * nu / (omega_r * denom)

        # İndeks (yaklaşık): n ≈ sqrt(ε_r)
        if eps_r_real < 0:
            # Overdense: tam rekleksiyon + absorpsiyon
            # Zayıflama kalınlıkla artar
            alpha = omega_p ** 2 * nu / (2 * omega_r * denom)
            att_db = 8.686 * alpha * thickness  # Nepers → dB
        else:
            # Underdense: kısmi absorpsiyon
            n_real = math.sqrt(max(0, eps_r_real))
            alpha = omega_p ** 2 * nu / (2 * omega_r * denom * max(0.01, n_real))
            att_db = 8.686 * alpha * thickness

        return att_db

    def activate(self, t):
        """Plazmayı aktifleştir (yüksek gerilim uygula)."""
        self.active = True
        self.activation_time = t

    def deactivate(self):
        """Plazmayı deaktifleştir."""
        self.active = False
        self.activation_time = None

    def density_at(self, positions: NDArray[np.floating]) -> NDArray[np.floating]:
        """Verilen konumlardaki plazma elektron yoğunluğunu (normalize) döndür.

        Arayüz: ParticleCloud.density_at() ile aynı.
        Döndürdüğü değer, effects.py'deki attenuation() fonksiyonuna beslenir.

        Returns:
            (N,) boyutunda array: her konum için normalize plazma yoğunluğu [0, 1]
        """
        if not self.active:
            return np.zeros(len(positions))

        pos = np.asarray(positions, dtype=float)  # (N, 2)
        result = np.zeros(len(pos))

        for i, p in enumerate(pos):
            # Her elektrota olan uzaklık
            dists = np.linalg.norm(self.electrodes - p[None, :], axis=1)  # (n_electrodes,)

            # En yakın elektrotun etki alanı
            # Gaussian dağılım: n(r) = n_peak * exp(-r² / (2 * σ²))
            sigma = self.plasma_radius
            weights = np.exp(-dists ** 2 / (2 * sigma ** 2))

            # Elektrotlar arası etkileşim (between electrodes → daha yüksek yoğunluk)
            if self.n_electrodes > 1 and len(dists) > 1:
                min_dist = np.min(dists)
                # Elektrotlar arası bölge → yoğunluk artışı
                for j in range(self.n_electrodes):
                    for k in range(j + 1, self.n_electrodes):
                        mid = (self.electrodes[j] + self.electrodes[k]) / 2
                        mid_dist = np.linalg.norm(p - mid)
                        # Ortadaki bölgeye ek yoğunluk
                        mid_weight = np.exp(-mid_dist ** 2 / (2 * (sigma * 0.7) ** 2))
                        weights[j] = max(weights[j], mid_weight * 0.8)

            # Toplam normalize yoğunluk
            total_weight = np.sum(weights)
            # Normalize: max 1.0
            result[i] = min(1.0, total_weight * self.peak_density / 1e15)

        return result

    def get_rf_attenuation_db(self, pos, thickness, freq_ghz=10.0):
        """Belirli bir konuda RF zayıflamasını dB cinsinden hesapla.

        Args:
            pos: (2,) konum vektörü
            thickness: plazma kalınlığı (m)
            freq_ghz: radar frekansı (GHz), default 10 (X-band)
        """
        if not self.active:
            return 0.0

        # O konumdaki elektron yoğunluğu
        density = self.density_at(pos[None, :])[0]
        n_e = density * self.peak_density  # m⁻³

        freq_hz = freq_ghz * 1e9
        return self._rf_attenuation_from_plasma(n_e, thickness, freq_hz)

    def step(self, dt):
        """Plazma durumunu güncelle.

        Plazma sürekli olarak HV tarafından beslendiği için bozunum yoktur
        (aerosolün aksine). Sadece küçük dalgalanmalar olabilir.
        """
        if not self.active:
            return

        # Plazma kararlı — sadece küçük fluktuasyonlar
        # (rüzgar, gaz akışı vb. etkiler)
        t = self.cfg.DT  # mevcut zaman adımı
        # Plazma yoğunluğunda %5 rassal dalgalanma
        # (Bu, effects.py'deki attenuation hesabını etkilemez çünkü density_at() gaussian)

    def integrity(self):
        """Plazmanın bütünlük skoru [0, 1]."""
        if not self.active:
            return 0.0
        return 1.0  # plazma aktifken her zaman tam yoğunlukta

    def summary(self):
        """Plazma durumu özeti."""
        omega_p = self._plasma_frequency(self.peak_density)
        omega_x = 2 * math.pi * 10e9  # X-band
        return {
            "peak_density_m3": f"{self.peak_density:.2e}",
            "plasma_freq_ghz": f"{omega_p / (2 * math.pi * 1e9):.2f}",
            "x_band_freq_ghz": "10.00",
            "overdense": omega_p > omega_x,
            "voltage_kv": self.voltage,
            "radius_m": self.plasma_radius,
            "n_electrodes": self.n_electrodes,
        }
