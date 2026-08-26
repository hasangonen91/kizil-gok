# KIZIL GÖK — Aşama 1: Laboratuvar Doğrulama Protokolü

**Versiyon**: 0.1  
**Tarih**: Ağustos 2026  
**Amaç**: Elektron bulutunun RF sönümleme etkisinin laboratuvar koşullarında kanıtlanması

---

## 1. Bilimsel Arka Plan

### 1.1 Hipotez
İletken kaplamalı mikrokürelerden oluşan yüklü aerosol bulutu, X-bant (8-12 GHz) radar sinyallerini **10 dB'den fazla** zayıflatır. Parçacık boyutu λ/10'un altındayken optik olarak şeffaf kalır.

### 1.2 Temel Fizik
- **RF zayıflama**: İletken tanecikler elektromanyetik dalga ile etkileşerek sinyali absorbe/saçar. Zayıflama yoğunluk, parçacık boyutu ve iletkenliğe bağlıdır.
- **Rayleigh saçılması**: Parçacık boyutu (d) λ/10'un altındayken optik olarak şeffaf: d < 40-70 nm可见光 için. Bizim aralık: 1-10 μm → optik olarak hafif pus, RF'de etkili.
- **İndüksiyon**: Hızlı hareket eden iletken nesne (füze gövdesi), yüklü buluttan geçerken dΦ/dt ile EMF indüklenir → elektronik devrelerde hasar.

### 1.3 Simülasyon Verisi (mevcut)
- `exp_speed.py` sonuçları: Yoğun duvar konfigürasyonu 600 m/s'ye kadar %100 etkisizleştirme
- Coulomb şişmesi bulgusu: parçacık yoğunluğu = N × q ÷ (Coulomb katsayısı × yayılma hacmi)
- Mevcut model: basitleştirilmiş RF zayıflama = COUNT / DENS_FULL

---

## 2. Aşama 1 Hedefleri

| # | Hedef | Ölçüm | Başarı Kriteri |
|---|---|---|---|
| H1 | RF sönümleme doğrulaması | VNA S21 ölçümü, X-bant | ≥ 10 dB zayıflama (10 kat güç kaybı) |
| H2 | Parçacık boyutu doğrulaması | Optik parçacık sayacı (OPC) | d50 < 8 μm, d99 < 15 μm |
| H3 | Şarj kalitesi | Faraday kabı + elektrometre | q/m > 50 μC/g |
| H4 | Şarj ömrü | Zaman serisi elektrometre | τ > 30 s (nem < %40 RH) |
| H5 | Simülasyon kalibrasyonu | Sim params → lab verisi eşleştirme | Kalibrasyon hatası < %20 |

---

## 3. Ekipman Listesi

### 3.1 RF Ölçüm Sistemi
| Ekipman | Model/Özellik | Kaynak | Tahmini Maliyet |
|---|---|---|---|
| VNA (Vector Network Analyzer) | 8-12 GHz, 2-port | ETÜ Elektronik veya kiralama | ₺15.000 (30 gün kiralama) |
| Horn anten (×2) | X-bant, 10-15 dBi | Satın alma | ₺8.000 |
| RF kablo + konnektör | SMA/3.5mm, LMR-240 | Satın alma | ₺3.000 |
| RF absorber panel | Piyano pedi benzeri, 10-20 dB | Alternatif: kalın battaniye | ₺2.000 |

### 3.2 Aerosol Üretim Sistemi
| Ekipman | Özellik | Kaynak | Tahmini Maliyet |
|---|---|---|---|
| Elektrostatik püskürtücü | 30-100 kV, 0.5-5 mL/dk | Palas/DEM veya özel imalat | ₺45.000 |
| Yüksek gerilim kaynağı | 0-100 kV DC, 1 mA | Satın alma | ₺25.000 |
| Aerosol depo + pompa | 1L paslanmaz, peristaltik | Satın alma | ₺8.000 |
| Toz/küre malzemesi | 1-5 μm iletken kaplamalı cam küre | Sigma-Aldrich / özel | ₺12.000 (500g) |

**Malzeme alternatifleri** (düşük maliyetli):
- **Grafit kaplamalı cam küre**: ~$20/g, iyi iletkenlik
- **Karbon nanotüp dispersiyonu**: daha ucuz ama daha zorualaşan
- **Demir oksit nanopartikül**: manyetik özellik ek avantaj

### 3.3 Karakterizasyon Ekipmanları
| Ekipman | Özellik | Kaynak | Tahmini Maliyet |
|---|---|---|---|
| Optik parçacık sayacı (OPC) | 0.3-10 μm aralık | Kiralama veya ETÜ | ₺20.000 (kiralama) |
| Faraday kabı + elektrometre | 1 fC hassasiyet | Satın alma | ₺18.000 |
| Nem/sıcaklık sensörü | ±%1 RH, ±0.5°C | Satın alma | ₺2.000 |
| Hız sensörü (opsiyonel) | Anemometre | Mevcut olabilir | ₺3.000 |

### 3.4 Test Alanı
| Öğe | Özellik | Maliyet |
|---|---|---|
| Test tüneli / kutu | 10-15m uzunluk, 1.5×1.5m kesit, kapalı | ₺15.000 (prefabrik konteyner) |
| Havalandırma | Kontrollü hava akışı (0-10 m/s) | ₺8.000 |
| Veri toplama sistemi | DAQ + PC + yazılım | ₺12.000 |

### 3.5 Yazılım
| Yazılım | Amaç | Maliyet |
|---|---|---|
| KIZIL GÖK simülatörü | Parametre optimizasyonu | ✅ Mevcut |
| GNU Radio / MATLAB | VNA veri analizi | ₺5.000 (MATLAB lisans) veya ücretsiz GNU Radio |
| Python + NumPy/SciPy | Aerosol modelleme | ✅ Ücretsiz |

---

## 4. Deney Düzeni

### 4.1 Genel Layout (üstten görünüm)
```
[HAVA GİRİŞİ] [FİLTRE] [PUŞKÜRTÜCÜ] [← 5m →] [TEST BÖLGE] [← 5m →] [FİLTRE] [EGZOZ]
                                    │              │              │
                              Faraday kabı    VNA Port 1    VNA Port 2
                              OPC + probe     (Horn Anten)  (Horn Anten)
```

### 4.2 Temel Akış
1. Aerosol püskürtücüsü test bölgesine yüklü parçacık bulutu gönderir
2. İki horn anten karşı karşıya, aralarında ~5m boşluk
3. Bulut bu boşlukta yoğunluk oluşturur
4. VNA, S21 (iletim) parametresini sürekli ölçer
5. OPC ve Faraday kabı parçacık özelliklerini ölçer
6. Veriler senkronize olarak kaydedilir

---

## 5. Deney Prosedürü

### 5.1 Hazırlık (Hafta 1-2)
1. Test tünelini kur, RF absorber panelleri yerleştir (refleksiyon azaltma)
2. Horn antenleri hizala, VNA kalibre et (open-short-load)
3. Aerosol püskürtücüsünü test et: akış hızı, droplet boyutu, kararlılık
4. Faraday kabı kalibrasyonu (bilinen yük ile)
5. Faraday kabı kalibrasyonu (bilinen yük ile)
6. OPC sıfırlama ve zero-count kontrolü

### 5.2 Deney 1: Boşluksuz Referans (Hafta 3)
- Bulut OLMADAN VNA S21 ölçümü
- Amaç: sistemin kendi zayıflamasını (kablo kaybı, anten yansıma) ölç
- Sonuç: S21_ref ≈ -5..-15 dB (sistematik offset)

### 5.3 Deney 2: RF Sönümleme Testi (Hafta 3-6)
**Parametre uzayı:**

| Parametre | Değerler | Sayı |
|---|---|---|
| Parçacık yoğunluğu | 3 seviye (düşük/orta/yüksek) | 3 |
| Parçacık boyutu | 2 tür (2μm, 5μm) | 2 |
| Şarj durumu | Yüklü (50kV) / Şarjsız (0kV) | 2 |
| Frekans | 8, 9, 10, 11, 12 GHz | 5 |

**Toplam koşu**: 3 × 2 × 2 × 5 = 60 koşu  
**Tekrar**: Her koşu 3 kez → **180 ölçüm**

Her koşu prosedürü:
1. Sistem stabilize (2 dk)
2. VNA sweep (100 nokta, IF bant genişliği 100 Hz)
3. OPC 30 saniye örneklem
4. Faraday kabı okuma
5. Bulut temizle (3 dk havalandırma)
6. Sonraki koşu

**Ölçülen**: ΔS21 = S21_bulut - S21_ref → **RF zayıflama dB**

### 5.4 Deney 3: Şarj Ömrü (Hafta 7)
- Tek yoğunluk seviyesinde püskürtme durdur
- 60 saniye boyunca her 2 saniyede bir S21 + elektrometre oku
- Şarjın zamanla azalma eğrisi → τ (tau) hesapla
- Nem ve sıcaklık kaydı

### 5.5 Deney 4: Rüzgar Etkisi (Hafta 8, opsiyonel)
- Havalandırma ile 0, 3, 6 m/s hava akışı
- Sönümleme >> Sedimantasyon hızlıysa etki azalır

---

## 6. Veri Analizi

### 6.1 Ana Çıktı: Zayıflama Haritası
- **Frekans vs. Zayıflama** eğrisi (şarjlı/şarjsız karşılaştırma)
- **Yoğunluk vs. Zayıflama** (lineer? logaritmik?)
- **Parçacık boyutu etkisi** (2μm vs 5μm)

### 6.2 Simülasyon Kalibrasyonu
Mevcut sim parametreleri (`DENS_FULL`, `LOCK_LOSS_RATE`) lab verisiyle eşleştirilir:
```
Ölçülen: 10 dB zayıflama @ 10 GHz, yoğunluk X parçacık/m³
Sim'de: DENS_FULL = X / 10^(10/10) = X/10 → yeniden hesapla
```

### 6.3 Rapor Çıktıları
1. Zayıflama haritası (grafik)
2. Kalibre edilmiş sim parametreleri
3. "Bu konsept X dB zayıflama sağlar" sonucu
4. Pub-müfredatık bulgu: Coulomb şişmesi + RF etkileşim

---

## 7. Bütçe

| Kalem | Tutar (₺) | Not |
|---|---|---|
| RF ekipmanı (VNA + anten + kablo) | 28.000 | VNA kiralama 30 gün |
| Aerosol sistemi (püskürtücü + HG) | 70.000 | En pahalı kalem |
| Karakterizasyon (OPC + Faraday) | 40.000 | OPC kiralama |
| Test alanı (tünel + havalandırma) | 35.000 | Prefabrik konteyner |
| Yazılım + lisans | 5.000 | MATLAB veya GNU Radio |
| Personel (6 ay, 1 araştırmacı) | 120.000 | TÜBİTAK bursu ile karşılanabilir |
| Tüketim malzemeleri | 15.000 | Aerosol, kablo, yedek parça |
| **Beklenmedik (%15)** | **43.000** | |
| **TOPLAM** | **356.000** | |

**Karşılaştırma**: TÜBİTAK 1512 biGG Phase 1: ~450.000 ₺ hibe → **tamamı karşılanabilir**

---

## 8. Zaman Çizelgesi

| Ay | Faaliyet | Çıktı |
|---|---|---|
| 1-2 | Ekipman temini + test alanı kurulumu | Hazır laboratuvar |
| 3 | Aerosol püskürtücü optimizasyonu | Kararlı bulut üretimi |
| 4-5 | Deney 2: RF sönümleme testleri (60 koşu) | Zayıflama verisi |
| 6 | Deney 3: Şarj ömrü + Deney 4: Rüzgar | τ + rüzgar verisi |
| 7-8 | Veri analizi + sim kalibrasyonu | Kalibre edilmiş sim |
| 9 | Rapor yazımı + patent başvuru | Aşama 1 tamamlandı |
| 10-12 | Aşama 2 planlama + SSB/TÜBİTAK sunumu | Fon secured |

---

## 9. Risk Değerlendirmesi

| Risk | Olasılık | Etki | Azaltma |
|---|---|---|---|
| VNA verisi beklenenden düşük | Orta | Yüksek | Yoğunluk artır, farklı malzeme dene |
| Aerosol püskürtücü stabil değil | Orta | Orta | Endüstriyel sprey firmasıyla prototip |
| Test alanı RF yansıması yüksek | Düşük | Orta | Absorber panel + referenced measure |
| Bütçe aşımı | Düşük | Orta | Öncelik sıralaması, kiralama |
| Hava koşulları (nem) | Düşük | Düşük | Kapalı test alanı + klima |

---

## 10. ETÜ İşbirliği Teklifi

### Neden ETÜ?
- Erzurum Teknik Üniversitesi Fizik / Elektronik bölümleri
- VNA ve RF laboratuvarı erişimi
- Araştırma görevlisi/öğrenci desteği
- TÜBİTAK başvurusunda üniversite onayı şart

### Teklif:
1. ETÜ Fizik Bölümü'ne resmi dilekçe (ortak Ar-Ge projesi)
2. Öğrenci projesi olarak 2-3 yüksek lisans/bitiş tezi
3. Yayın hedefi: Uluslararası hakemli dergide makale (物理review benzeri)
4. Maliyet paylaşımı: KIZIL GÖK ekipman, ETÜ laboratuvar + personel

### İletişim:
- ETÜ Fizik Bölümü Başkanlığı
- Konu: "Yüklü aerosol bulutlarının RF zayıflama özelliklerinin deneysel incelenmesi"
- Makale başlığı önerisi: *"Electromagnetic Attenuation Properties of Charged Conductive Microsphere Aerosols for Soft-Kill Active Protection Systems"*

---

## 11. TÜBİTAK 1512 biGG Başvuru Stratejisi

### Uygunluk:
- BiGG (Bireysel Genç Girişimci) programı
- Savunma teknolojisi kotası mevcut
- Fikri mülkiyet tescili + deneysel kanıt = güçlü başvuru

### Gerekli Belgeler:
1. İş planı (şablon TÜBİTAK'ta mevcut)
2. Ekibin özgeçmişi
3. Prototip/kanıt kavramı (KIZIL GÖK simülatörü + bu protokol)
4. Pazar analizi
5. Bütçe tablosu

### Zamanlama:
- Sonbahar dönemi başvurusu (Eylül-Ekim)
- Sonuç: ~3 ay içinde
- Fondan yararlanma: ~12 ay içinde

---

## 12. Fikri Mülkiyet

### Patent Başvurusu:
- **Başlık**: "Yüklü aerosol bulutu ile aktif koruma sistemi ve yöntemi"
- **Başvuru yeri**: TÜRKPATENT (faydalı model veya patent)
- **Zamanlama**: Lab testlerinden ÖNCE (simülasyon verisi + konsept yeterli)
- **Maliyet**: ~₺5.000-8.000 (avukat + başvuru ücreti)

### Ticari Sır:
- Bu protokol gizli tutulmalı
- GitHub repo PRIVATE kalmalı
- Paylaşım: sadece ETÜ hocaları + TÜBİTAK evaluatorleri ile

---

*Bu doküman KIZIL GÖK projesinin Aşama 1 laboratuvar doğrulama planıdır.  
Hazırlayan: Murat Kızıl — KIZIL GÖK Teknik Lideri  
Onaylayan: Hasan Gönen — KIZIL GÖK Kurucu*
