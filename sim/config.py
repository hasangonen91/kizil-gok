# -*- coding: utf-8 -*-
"""KIZIL GÖK simülasyon parametreleri (SI birimleri: metre, saniye)."""

SEED = 42

DT = 0.02
SIM_TIME = 14.0
RECORD_EVERY = 2          # her N adımda bir kare kaydet

# ---- Parçacık bulutu (elektron duvar) ----
N_PARTICLES = 900
CHARGE_MIX = 1.0          # + yük oranı (1.0 = hepsi aynı işaret, 0.5 = yarı yarıya)
Q0 = 2.0                  # başlangıç yükü
COULOMB_K = 7.0          # parçacık arası itme/çekme katsayısı
SOFTENING = 1.5           # yakın mesafe patlamasını engelleyen yumuşatma (m)
DRAG = 0.80               # hava sürtünme katsayısı (1/s)
GRAVITY = 2.5             # etkili yerçekimi (yüklü aerosol kabullenmesi, m/s^2)
CHARGE_DECAY_TAU = 25.0   # korona boşalmasıyla yük kaybı zaman sabiti (s)

# yer istasyonu yüksek güçlü RF bakım isini (bulutu iyonize tutar)
RF_BEAM = False
RF_BEAM_TAU = 250.0       # isin acikken yuk kaybi zaman sabiti (s)

# iki serpici koridoru kuşatır (İHA + kule), düz yelpaze atış
DISPENSERS = [
    {"pos": (-380.0, 160.0), "cone_deg": (166.0, 198.0), "speed": (170.0, 365.0)},
    {"pos": (-900.0, 155.0), "cone_deg": (-18.0, 14.0), "speed": (150.0, 340.0)},
]

# ---- Füze ----
MISSILE_START = (-3100.0, 430.0)
MISSILE_SPEED = 300.0
NAV_GAIN = 4.0            # orantılı seyrütlefer kazancı
TARGET = (0.0, 60.0)      # korunanan varlık (radar masti vb.)
HIT_RADIUS = 22.0         # savaş başlığı tesir yarıçapı (m)

BULUT_DEPLOY_T = 1.0      # bulut fırlatma anı (füze algılanınca)

# ---- Etki modeli (seeker bozulumu) ----
DENSITY_RADIUS = 48.0     # yerel yoğunluk ölçüm yarıçapı (m)
DENS_FULL = 15.0          # tam sinyal kaybına karşılık gelen yerel yüklü parçacık sayısı (aerosol modu)
PLASMA_DENS_FULL = 1.0    # plazma modu için: density_at() 1.0 döndüğünde tam sinyal kaybı
LOCK_LOSS_RATE = 1.05     # tam zayıflamada kilit kaybı hızı (1/s)
LOCK_RECOVER_RATE = 0.10  # temiz havada toparlanma (1/s)
SEEKER_NOISE = 3.0        # kilit 0 iken maksimum güdüm gürültüsü (rad/s)
SEEKER_BIAS_RATE = 0.32   # körlükte yanilsama kaymasi difuzyonu (rad/s^0.5)
GUIDE_AUTHORITY_FLOOR = 0.30  # kilit 0 iken kalan güdüm otoritesi oranı

BURN_COUNT_MIN = 8.0      # induksiyon yanması için gereken yerel parçacık sayısı
BURN_K = 1.30             # yanma olasılık katsayısı (1/s)

FUZE_SAFE_P_BURNOUT = 0.85  # seeker yaninca ayni surun fuze S&A devresini de yaklama olasiligi

# ---- Plazma koruma sistemi (aerosol yerine) ----
PLASMA_MODE = True  # True = plazma, False = aerosol (eski mod)

# Elektrot yerleşimi: füzenin uçuş koridoruna plazma duvarı (x, metre)
# Füze (-3100, 430)'den (0, 60)'a alçak açıyla geliyor
# Plazma duvarı füzenin geçeceği noktaya yerleştirildi
PLASMA_ELECTRODES = [
    (-1200.0, 280.0),  # Sol uzun menzil — füze buradan geçer
    (-800.0, 230.0),   # Sol orta menzil
    (-400.0, 180.0),   # Sol kısa menzil
    (0.0, 130.0),      # Merkez — aracın tam önü
    (400.0, 100.0),    # Sağ kısa menzil
]

PLASMA_VOLTAGE = 100.0         # Uygulanan gerilim (kV) — pulsed power ile mümkün
PLASMA_RADIUS = 120.0          # Elektrot etki yarıçapı (m) — Gaussian σ
PLASMA_GAS_DENSITY = 1.0       # Normalize gaz yoğunluğu (1.0 = standard hava)
PLASMA_COLLISION_FREQ = 5e9    # Elektron-çarpışma frekansı (Hz) — X-band için kritik

# Plazma RF sönümleme parametreleri
PLASMA_FREQ_GHZ = 10.0         # Hedef radar frekansı (GHz) — X-band
PLASMA_THICKNESS = 25.0        # Plazma kalınlığı (m) — füzeyi geçeceği yol

# Plazma aktifleşme zamanlaması
PLASMA_ACTIVATE_T = 0.5        # Füze algılanınca plazmayı aktifleştirme (s)
