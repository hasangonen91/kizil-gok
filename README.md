# BULUT-KALKAN ⚡🛡️

**Elektron Bulut Aktif Koruma Sistemi — Konsept Simülatörü**

Gelen füzeye karşı korunan varlığın önüne **yüklü parçacık bulutu (elektron duvar)** serpen yumuşak öldürme (soft-kill) sistemi konseptinin fizik simülasyonu ve animasyonu.

Füze vurulmaz; **görmez, şaşar veya arayıcisi yanar.**

![poster](media/poster.png)

## Konsept

İki serpici (İHA + kule), gelen füzenin son yaklaşım koridorunu kuşatır ve yüklü iletken aerosol bulutu serper. Bulut:

1. **RF sinyali zayıflatır** → seeker data-link'i ve radar dönüşü körelir
2. **Yanılsama yaratır** → körleşen seeker yanlış noktaya kilitlenir, güdüm sistematik sapar
3. **Induksiyon akımı bindirir** → yoğun buluttan geçen arayıcı devresi yanabilir (seeker burnout)

## Fizik Modeli

| Bileşen | Model |
|---|---|
| Parçacık dinamiği | Coulomb itişimi (yumuşatılmış) + hava sürüklenmesi + etkili yerçekimi |
| Yük bozunumu | Korona boşalması, üstel azalma (`tau = 25 s`) |
| Füze güdümü | Orantılı seyrükleme (PN, `N = 4`), kilitle azalan otorite |
| Seeker bozulumu | Yerel yüklü yoğunluk → RF zayıflaması → kilit kaybı + yanilsama kayması (bias random walk) |
| Seeker yanması | Yoğunluk eşiği üstünde olasılıksal induksiyon yanması |

## Çalıştırma

```bash
pip install -r requirements.txt

# headless simülasyon (farklı tohumlar farklı senaryolar üretir)
python3 run_sim.py 42

# sinematik video (gece sahnesi, HUD, slow-motion angajman)
python3 render_cinematic.py 99 media/demo_sinematik.mp4

# eski stil bilimsel animasyon
python3 animate.py 99 media/demo.mp4
```

Python 3.11+, numpy, matplotlib, pillow, ffmpeg gerektirir.

## Sistem Mimarisi (gerçek dünya karşılığı)

| Aşama | Teknoloji |
|---|---|
| Erken uyarı / hedefleme | IR uydu + yer bazlı fazlı array radar |
| Parçacık şarjı | Serpici nozulunda korona deşarjı (elektrostatik püskürtme mantığı, 30-100 kV) |
| Bulut bakımı (opsiyonel) | Yer istasyonu yüksek güçlü RF bakım ışını → `sim/config.py` içinde `RF_BEAM = True` |
| Etki | RF zayıflaması + seeker yanılsaması + induksiyon yanması |

## Senaryo Sonuçları

Aynı parametrelerle farklı tohumlar gerçekçi dağılım verir:

- `SAPTI — bulut füzeyi kör etti` → kilit kaybı + yanılsama füzyonu saptırdı
- `ÇAKILDI — SAVAŞ BAŞLIĞI ETKİSİZ (dud)` → induksiyon akımı seeker'ı ve fünye S&A devresini birlikte yaktı; füze patlamadan çakıldı
- `VURDU — bulut yetersiz` → yoğunluk/ zamanlama yetmedi (tesisat parametresi)

Parametreler `sim/config.py` içinde; duvar yoğunluğu, yük karışımı (+/-), serpici yerleşimi, seeker eşikleri ve fünye emniyet olasılığı oynanabilir.

### Görünürlük notu

Gerçek sistemde duvar **gözle görünmez**dir: 1-5 mikron iletken mikro-küreler Rayleigh rejiminde saçılır (optik olarak şeffaf), oda sıcaklığında IR imzası yoktur, λ/10 altı boyut sayesinde düşman radarında parlak blob oluşturmaz. Simülasyon görsellerindeki ışıltı yalnızca izleyiciye anlatım amaçlıdır.

## Hız Deneyi (exp_speed.py)

"Yüksek hızlı füze buluttan fazla hızlı geçemez mi?" sorusunun sim cevabı — varış anı sabit, yalnızca geçiş hızı değişir (5 tohum):

| Hız | Taban duvar | Yoğun duvar (2x parçacık, K↓, q↑) |
|---|---|---|
| 300 m/s | %40 | **%100** |
| 600 m/s | %0 | **%100** |
| 1200 m/s | %0 | **%40** |

Bulgular:
- Etki süresi = duvar derinliği ÷ füze hızı, ama RF körlüğü anlıktır (EM alan ışık hızında işler) ve induksiyon EMF'si geçiş hızıyla ARTAR
- Kritik keşif: parçacık sayısını tek başına artırmak Coulomb şişmesiyle duvarı SEYRELTIYOR; yoğunluk = parçacık × yük ÷ itişim dengesiyle yönetilmeli
- Süpersonik hedefler için yol haritası: yoğun + katmanlı duvar kombinezonu ve RF bakım ışını

```bash
python3 exp_speed.py
```

## Yol Haritası

- [ ] 3B genişletme + rüzgar alanı
- [ ] Aynı işaretli / karışık yük (+/-) karşılaştırmalı deneyler
- [ ] Çoklu füze salvosu ve maliyet-değişim optimizasyonu
- [ ] Monte Carlo toplu koşucu (isabet istatistikleri grafiği)
- [ ] Serpici balistiğinin gerçek roket modeliyle değiştirilmesi

## Not

Bu depo **konsept düzeyinde eğitim ve Ar-Ge simülasyonudur**; gerçek bir silah tasarımı içermez.
