# KIZIL GÖK — Aşama 1 Bütçe Optimizasyonu (₺356k → ₺83k)

**Amaç**: İlk laboratuvar doğrulamasını mümkün olan en düşük maliyetle yapmak
**Hedef**: "Bu konsept işe yarar mı?" sorusuna tek bir.measure ile cevap almak

---

## Neden Bu Kadar Ucuz?

Temel strateji: **Üniversite altyapısını + mevcut ekipmanı + ücretsiz yazılımları kullan**. 

Profesyonel savunma laboratuvarı değil, **üniversite araştırma laboratuvarı** koşullarında, akılcı mühendislik ile.

---

## 1. Aerosol Üretim Sistemi (₺70k → ₺15k)

### Eski Plan: Profesyonel Elektrostatik Sprey
- Palas GF-26 aerosol jeneratörü: ~₺45k
- 0-100 kV HG kaynağı: ~₺25k

### Yeni Plan: Modifiye Endüstriyel Ekipman
**Malzemeler:**
- Elektrostatik toz boyama tabancası (amatör/ev tipi): ~₺3,000
  - Amazon/HePSAT: "electrostatic paint sprayer 30kV"
  - Zaten korona deşarj + yükleme yapıyor!
  - Toz formunda malzeme püskürtür
- Yüksek gerilim modülü (EMS/alternatif): ~₺2,000
  - 0-50 kV DC, 1 mA (korona deşarj için yeterli)
  - Modifiye elektrik şofbeniden veya HG modulesinden
- Toz/malzeme:
  - **En ucuz seçenek**: Karbon siyahı (lamp black) tozu: ~₺200/kg
  - **İyi seçenek**: Grafit tozu (kimya market): ~₺2,000/kg
  - **Mükemmel**: iletken kaplamalı cam küre (Sigma-Aldrich): ~₺12,000/500g
- Besleme sistemi: Basit huni + hava kompresörü (mevcut)

**Nasıl çalışır:**
1. Toz tabancasının haznesine karbon/grafit tozu doldur
2. Tabanca 30-50 kV ile otomatik yüklüyor (zaten built-in korona)
3. Nozuldan çıkan toz bulutu → iletken ve yüklü
4. Hedef: >50 μC/g yüklülük (tabancanın kendi şarjı yeterli olabilir)

**Test**: Önce şarjsız (0kV) → sonra yüklü (50kV) karşılaştırma. Fark varsa yöntem çalışıyor.

**Risk azaltma**: Tabancayı 1 hafta önce al, evde dene. Yükleme kalitesini basit Faraday kabı ile ölç.

---

## 2. RF Ölçüm Sistemi (₺28k → ₺12k)

### Eski Plan: 30 Günlük VNA Kiralama
- VNA (30 gün): ₺15k
- Horn anten (2 adet): ₺8k
- RF kablo: ₺3k

### Yeni Plan: 5 Günlük Yoğun Batch + Ücretsiz Alternatifler

**VNA (5 gün kiralama): ~₺8,000**
- Hafta sonu dahil 5 gün
- Tüm ölçümleri bu süreye sığdır
- Planlama: 1-2 hafta hazırlık, sonra " measurement sprint"

**Horn anten**: ~₺4,000
- 2 adet X-bant horn anten
- Satın alma (kiralamadan ucuz, tekrar kullanılabilir)
- Çin'den: AliExpress "X-band horn antenna 10GHz" ~$50/adet

**Alternatif (sıfır maliyet)**: Eğer ETÜ'de antenna varsa → directly kullan

**DIY Alternatif (maliyet ~₺2,000)**:
- 2 adet mikrodalga ocağı magnetronu + dalga kılavuzu
- Magnetron ~10 GHz üretebilir (çok ucuz, ama kalibrasyon zor)
- **Önerilen**: VNA ile git, temiz veri al. Magnetron acil durum planı.

---

## 3. Karakterizasyon Ekipmanları (₺40k → ₺3k)

### Eski Plan
- OPC (kiralama): ₺20k
- Faraday kabı + elektrometre: ₺18k

### Yeni Plan: DIY + Üniversite Ekipmanı

**Faraday kabı (DIY, ~₺500)**:
- 30cm küp bakır ağ (Elektromanyetik kalkan mağazası / eBay)
- Faraday cage retainer ile topraklama
- İçi boş, bir delikten probe girer

**Yük ölçümü (₺2,500)**:
- Electret mikrofonu modifiyesi veya
- Basit elektrometre devresi (op-amp +高阻抗 giriş)
- Arduino + yüksek阻抗 giriş ile Osiloskop → yüklü parçacık akımı ölçümü
- **En ucuz**: Multimetre (zaten var) + direnç → akım ölç → yük hesabı

**OPC (sıfır maliyet)**:
- ETÜ Fizik Bölümü'nde optik laboratuvarı olabilir
- Partikül boyutu için alternatif: Mikroskop + sayma (düşük hız ama ücretsiz)
- Ya da published data kullan (Sigma-Aldrich katalog değerleri)

---

## 4. Test Alanı (₺35k → ₺5k)

### Eski Plan: Prefabrik Konteyner
- Konteyner: ₺15k
- Havalandırma: ₺8k
- DAQ: ₺12k

### Yeni Plan: Üniversite Altyapısı

**ETÜ'den istenen alan**:
- Boş bir sınıf veya atölye (10m uzunluk, kapalı)
- Havalandırma: Mevcut pencere + fan (eríaşımı için)
- Ya da kapalı koridor / laboratuvar

**DAQ (₺5k)**:
- Laptop + Arduino + Python
- Sensörler: Termokupl (nem/sıcaklık), multimetre (yük)
- Veri toplama: basit Python scripti (zaten yazdık)

**Gerçek maliyet**: Sadece ufak düzenlemeler + kablo/askı

---

## 5. Personel (₺120k → ₺20k)

### Eski Plan: Tam Zamanlı Araştırmacı (6 ay)

### Yeni Plan: Öğrenci Projesi + TÜBİTAK Desteği

**ETÜ'den 2-3 öğrenci**:
- Yüksek lisans tezi: "Yüklü aerosol bulutlarının RF karakterizasyonu"
- Bitirme projesi: "Elektrostatik aerosol püskürtücü prototipi"
- Bitirme projesi: "RF zayıflama ölçüm sistemi tasarımı"

**Avantajlar**:
- Bedava iş gücü (tez/proje için zaten yapıyorlar)
- TÜBİTAK 2209/2242 ile öğrenci bursu (~₺12k/ay)
- Tez danışmanı: ETÜ Fizik hocası (bedava, akademik kariyer için gerekli)
- Sonuç: Tez + veri + potansiyel yayın

**Hasan'ın rolü**: Proje yöneticisi + teknik lider + veri analizi

---

## 6. Yazılım (₺5k → ₺0)

### Eski Plan: MATLAB Lisansı

### Yeni Plan: Açık Kaynak
- **GNU Radio**: SDR tabanlı RF analiz (ücretsiz)
- **Python + NumPy/SciPy**: Veri analizi (zaten mevcut)
- **QUCS**: Devre simülasyonu (ücretsiz)
- **KIZIL GÖK simülatörü**: Zaten hazır!

---

## 7. Tüketim Malzemeleri (₺15k → ₺8k)

Kalem bazında:
- Aerosol tozu (karbon/grafit): ₺2,000
- RF kablo ve konnektörler: ₺2,000
- Bakır ağ (Faraday): ₺500
- Elektronik malzeme (devre): ₺1,500
- Kimyasal malzeme (temizlik): ₺500
- Baskı/çikolata/fotokopi: ₺1,500

---

## OPTİMİZE BÜTÇE TABLOSU

| Kalem | Detay | Maliyet |
|---|---|---|
| **Aerosol** | Boya tabancası + HG + toz | ₺15,000 |
| **RF** | VNA 5 gün + 2 anten + kablo | ₺12,000 |
| **Ölçüm** | DIY Faraday + devre + Arduino | ₺3,000 |
| **Alan** | Üniversite mevcut altyapı | ₺5,000 |
| **Personel** | Öğrenci projeleri (TÜBİTAK bursu) | ₺20,000 |
| **Yazılım** | Açık kaynak (GNU Radio, Python) | ₺0 |
| **Tüketim** | Toz, kablo, devre, malzeme | ₺8,000 |
| **Beklenmedik (%15)** | | ₺10,000 |
| **TOPLAM** | | **₺73,000** |

**TÜBİTAK 1512 Phase 1**: ~₺450,000 hibe → **bütçenin 6 katı fazlası** var!

---

## Hangi Maliyet Kesenmez?

**Kesilemez (kritik)**:
- VNA ölçümü (sonuç buradan geliyor)
- Aerosol üretimi (deneyin kalbi)
- En az 1 hassas yük ölçümü

**Kesilebilir/ertelenebilir**:
- OPC (partikül boyutu published data ile idare edilir)
- Tam test alanı (koridor/sınıf yeterli)
- Tam zamanlı personel (öğrenci projesi ile karşılanır)

---

## İlk Adım: Sıfır Maliyetli Hazırlık (Bu Hafta)

1. **Simülatörü kalibre et**: Published aerosol RF attenuation verileri ile sim parametrelerini ayarla
   - Chaff datasheet'lerinden dB/m değerleri → sim'e gir
   - Bu bedavaya "sim ne kadar gerçekçi?" sorusuna cevap verir

2. **ETÜ Fizik Bölümü'nü ara**: "RF ölçüm laboratuvarınız var mı? VNA erişimi mümkün mü?"
   - Bir e-posta, sıfır maliyet, yüksek getiri

3. **Boya tabancasını test et**: online sipariş et, evde karbon tozu ile dene
   - Yükleme oluyor mu? Ne kadar yoğunluk? Faraday kabı ile ölç.

---

## Sonuç

**₺356k → ₺73k** (yaklaşık %80 tasarruf)

İlk doğrulama deneyi **教研项目 bütçesine** sığar. Büyük savunma firmalarının kapılarını çalmanın ön koşulu zaten bu değil — **ilk veriyi ucuz al, sonra ölçeklendir**.

Asıl pahalı olan aşama 2-3 (prototip + saha testi) — o da TÜBİTAK + SSB fonlaması ile karşılanır.

Ne dersin Yüce Zalim? Bu optimize bütçeyle yola devam mı? 🎯
