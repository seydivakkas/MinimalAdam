# P5 — Otomatik Görsel Kalite Denetimi

P5, **kaynak tanımlı P3/P4 teknik şemaları** ve **üretilmiş PNG dosyaları** için birbirinden ayrı, şeffaf kural kümeleri kullanır. Açıkça gösterilmeyen bir kalite puanı, yapay zekâ görsel algısı, OCR, Türkçe imla veya gerçek sistem semantiği doğrulaması yapılmaz.

## 1. Editördeki teknik şema QA

**Dosya:** `editor/quality.mjs` — aynı modül tek dosyalık `editor/offline.html` içine gömülmüştür.

- P3 JSON şeması: kimlikler, düğüm/ok sınırları, Türkçe NFC ve etiket uzunluk kısıtları (mevcut P3 kontrolleri korunur).
- Düğüm kutusu metni: gerçek tarayıcı font metriklerinden türetilen genişlik kutuyu aşabilir mi?
- Bağlantının başka bir düğüm üzerinden geçmesi ve bağlantıların kesişmesi.
- Bağlantı etiketinin kutu veya kenarla çakışması.
- Bağlantısız düğümler ve parçalı grafik.
- MinimalAdam'ın elinin seçtiği oka uzaklığı; karakter gövdesi ile kutu çakışması.
- Kutuların toplam alanına göre yaklaşık yoğunluk: **piksel boş alan yüzdesi değildir**.
- Çizim kaynağı değiştirildiğinde önceden verilmiş QA uyarı onayı sıfırlanır.

**Durum sözleşmesi**:

| Durum | Otomatik testin anlamı | Dışa aktar |
|---|---|---|
| `FAIL` | En az bir kaynak/şema hatası | Engellenir |
| `REVIEW` | Şema geçerli, geometrik/yerleşim uyarısı var | İncelenip açıkça onaylanmadan engellenir |
| `PASS` | Tanımlı otomatik kurallar sorun bulmadı | Teknik dosya dışa aktarılabilir; manuel kontrol yine gerekir |

`REVIEW` bir kullanıcı onayıyla dışa aktarılabilir. Rapor, bu onayın verilip verilmediğini içerir; onay semantik doğruluk iddiası değildir. Uyarılar ve `FAIL` bulguları *kaynak değişmeden* yeniden değerlendirilir.

İş akışı: düğüm/okları düzenle → sağdaki **P5 QA panelini** aç → bulguya basarak ilgili nesneyi seç → uyarıyı düzelt veya gerekçesini incele → **QA raporu indir** → SVG/PNG/JSON dışa aktar.

**Rapor biçimi:** `*-qa-report.json`, `p5-qa-v1`. `limits`, `metrics`, `issues`, `summary`, `manualChecks` ve `provenance.sourceProject` alanlarını içerir. Rapor durumları deterministiktir; görünüm tarayıcı fontuna bağlı olduğu için metin genişliği platforma göre farklılaşabilir.

## 2. PNG görsel ölçümleri

**Komut:** `tools/inspect_render.py` veya Codex Skill klasöründeki `scripts/inspect_render.py`.

```powershell
python -m pip install -r requirements.txt
python .\tools\inspect_render.py .\examples\technical\generated\03-ml-pipeline.png --report .\outputs\03-ml-qa.json
```

Çıktı `p5-png-v1` JSON raporudur. Pillow kullanır ve 4 piksel aralıklı örneklemeyle bunları kontrol eder:

- PNG biçimi ve 1600×900 boyut.
- Beyaz yakın piksel oranı (`blankFraction`), hedef en az %35.
- Köşelerde saf beyaz yakın alanın oranı.
- Doygun renklere göre siyah/turuncu/kırmızı/mavi paletinden sapma.
- Boş tuval tespiti, yaklaşık mürekkep sınır kutusu alanı.

Bu ölçümler bir görsel üretim modelini, OCR'yi veya internete erişimi **gerektirmez**. PNG okunamıyorsa veya boyutu yanlışsa `FAIL`; estetik gösterge sınır dışındaysa `REVIEW`; ölçümler uygunsa `PASS` döner. `FAIL` çıktısında araç durum kodu 2 ile çıkar; `REVIEW` raporu ayrıca değerlendirilmelidir. Piksel yüzdeleri örnekleme nedeniyle **yaklaşıktır**.

## 3. Otomatik doğrulanamayanlar

JSON raporundaki aşağıdaki maddeler özellikle `NOT_VERIFIED` kalır:

1. Düğümler, oklar ve veri akışı, kullanıcının **gerçek** kaynak koduyla eşleşiyor mu?
2. Karakterin özgünlük, kimlik ve eylemi görsel açıdan tutarlı mı?
3. Mecazın anlamı, estetik ve içerik hiyerarşisi yeterli mi?
4. Nihai fontlar kullanıcı bilgisayarında beklenen Türkçe harflerle render ediliyor mu?

P2 serbest illüstrasyonların PNG'leri de **raster** kontrolünden geçirilebilir. Ancak P5'in **graf geometrisi** kontrolleri yalnız P3/P4 kaynak şemaları için geçerlidir. Serbest illüstrasyonda nesne ile metin arasındaki anlamsal ilişki otomatik kanıtlanamaz.

## 4. Yeniden üretilebilir testler

```powershell
python -m unittest discover -s tests -p 'test_*.py'
node --test tests/js/*.test.mjs
python tests/e2e_p4.py
python tests/e2e_p5.py
python tools/validate_p4.py
python tools/validate_p5.py
```

`node` yalnız geliştirici testleri içindir; **kullanıcının editörü çalıştırması için Node gerekmez**. `tests/e2e_*.py` Chromium + Playwright gerektiren geliştirici testleridir ve üretim kullanımı için şart değildir.

Lisans: özgün projenin MIT lisansı ve Ian atfı korunur. İmgeler üzerinde yazı sözcüklerini otomatik okumak/kanıtlamak gibi bir işlev vaat edilmez.
