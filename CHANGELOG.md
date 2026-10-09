## v0.6.1 — Windows Cairo DLL uyumluluk düzeltmesi (2026-10-10)

- **P0:** Windows Python 3.14 üzerinde `cairocffi` / `cairo-2.dll` bulunamaması nedeniyle durdurulan yayın yolunu düzeltti.
- P3 PNG rasterlaştırıcısı CairoSVG yerine, bağımsız `tools/raster_pillow.py` / Skill kopyası üzerinden Pillow kullanıyor.
- Python bağımlılık listelerinden CairoSVG çıkarıldı; P3 örnek PNG'leri ve SHA256 manifestleri yeniden üretildi.
- Testlerde makineye bağlı fontlar için platformlar arası bayt eşitliği kaldırıldı; aynı ortamda tekrarlanabilirlik ve Cairo olmayan ortam doğrulaması eklendi.
- Windows CI Python 3.12 ve 3.14 matrisi kullanıyor. Gerçek Windows sonuçları GitHub'da iş akışı tamamlanınca doğrulanacak.
- Kaynak proje lisansı, atıf ve JSON/SVG/PNG veri sözleşmesi korundu.

# MinimalAdam — Sürüm Geçmişi

## v0.6 — Yeniden adlandırma ve GitHub hazırlığı

- Proje, uygulama, Codex Skill, başlatıcı, karakter adı ve görünür UI **MinimalAdam** olarak yeniden adlandırıldı.
- `minimaladam` JSON karakter alanı ve `minimaladam-editor-v1` proje kimliği yeni biçimdir. Eski `xiaohei` alanı ve eski SVG metadata içe aktarımı geçiş uyumluluğuyla korunur.
- Windows üzerinde çalışacak GitHub Actions kabul testi ve GitHub yayın betiği eklendi. Windows sonuçları ancak Windows üzerinde çalıştırıldıktan sonra kabul edilir.
- Üçüncü tarafın MIT lisansı ve Ian atfı korundu.

# Değişiklik günlüğü

## v0.5 — P5 Kalite Kapısı (2026-10-09)

- P3/P4 teknik grafikleri için test edilebilir, açıklanabilir ve yerel otomatik QA motoru.
- PASS/REVIEW/FAIL durumları, incelenebilir bulgu listesi ve kaynak projeyi de içeren JSON QA raporu.
- Uyarı onayı olmadan dışa aktarmama; proje değişikliklerinde onayı sıfırlama.
- Türkçe metin taşması, kaynak graf bütünlüğü, ok-kutu/ok-ok çakışmaları ve MinimalAdam temas kontrolü.
- PNG dosyaları için gerçek piksel ölçümüne dayalı (beyaz alan/palet/boş tuval) bağımsız CLI.
- Pozitif ve negatif otomatik testler; Chromium üzerinde uyarı/onay/dışa aktarma döngüsü.
- Otomatik ölçülemeyen dört kontrol açıkça NOT_VERIFIED bırakılır; OCR veya estetik kalite garantisi yoktur.


## v0.4 — P4 MinimalAdam Studio (2026-10-09)

- Çevrimdışı çalışan 3 panelli, Türkçe, tarayıcı tabanlı grafik editörü eklendi.
- P3 JSON ile kaynak uyumu; düğüm sürükleme ve ekleme/silme; bağlantı/ara nokta/etiket/karakter düzenleme.
- Üç görsel stil, geri al/ileri al, proje JSON, P3 JSON, metadata içeren SVG, PNG kaydı.
- Tek dosyalık `editor/offline.html`, Windows çift tık başlatıcısı ve localhost opsiyonu.
- P4 çekirdek ve gerçek Chromium etkileşim testleri; P1/P2/P3 testleri korunur.
- Eski P3 SVG kurtarma yaklaşık; mod/eylem kaybına dair kullanıcı uyarısı gösterilir.
- Sınırlar: otomatik graf yerleşimi, kompleks routing, kaynak kod analizinden mimari çıkarma, CAD ve semantik doğrulama yok.


## v0.3 — P3 Teknik Çizim Modu (2026-10-09)

- Dört mod eklendi: `architecture`, `data-flow`, `ml-pipeline`, `engineering-system`.
- JSON tanımlı doğrulanabilir düğüm/kenar sistemi ve semantiği tanımlı bağlantılar.
- P1/P2'nin karakter/renk dili korunarak sade vektörel şemalar.
- Her şema için yazısız SVG, Türkçe metin katmanı SVG, tam düzenlenebilir SVG, PNG ve SHA-256 manifest.
- Kırpılma, metin glif eksikliği, düğüm çakışması, üçüncü düğümü delen ok, yinelenen düğüm/bağlantı ve karakter-bağlantı uzaklığı kontrolleri.
- 4 temsili örnek, teknik rehber, yeni testler ve Skill klasöründe kendi araçlarını içeren kurulum.
- Sınır: gerçek mühendislik/topoloji doğruluğu kullanıcı kaynağından manuel doğrulanmalıdır. Tam otomatik routing veya CAD simülasyonu yoktur.

# Değişiklik Günlüğü

## TR v0.1 — 2026-10-09

**Kapsam:** Özgün işlevsel tasarım korunarak Türkçe yerelleştirme.

- Beceri adı ayrı tutuldu: `minimaladam`.
- `SKILL.md` Türkçeye uyarlandı, dil varsayılanı Türkçe yapıldı.
- Beş temel referans belgesi Türkçeye uyarlandı.
- `agents/openai.yaml` görüntülenen ad, açıklama ve başlangıç istemi Türkçeleştirildi.
- `README.md` ve örnek kullanım istemleri Türkçe olarak yeniden düzenlendi.
- Türkçe karakter, kısa etiket ve görsel kalite kontrol kuralları açıklaştırıldı.
- MIT lisansının özgün metni aynen korundu; yaratıcı atfı eklendi.
- Windows için kurulum betiği ve statik paket denetleyicisi eklendi.

**Bilerek kapsam dışında bırakılanlar:** Özgün PNG/JPG örneklerinin dağıtımı veya Türkçeleştirilmesi, bağımsız resim modeli, SVG editörü, gelişmiş teknik mimari diyagramları, GitHub'a gönderim.

**İncelenen kaynak:** https://github.com/helloianneo/ian-xiaohei-illustrations — `main` dalı, GitHub ağaç kimliği `4102eb807f03bcb6e538a16e8b31b41db8b5b954` (2026-10-09 tarihinde incelendi).

## TR v0.2 — 2026-10-09

**P1 — Özgün Türkçe örnekler ve karakter tutarlılığı**

- Üç özgün yazısız 16:9 SVG sahnesi (bilgi süzme, bağlantı onarma, kanıta dayalı karar) ve nihai Türkçe PNG örnekleri eklendi.
- Tek `#minimaladam` SVG sembolü üç sahnede de kullanıldı; karakterin görünür gövdesi sabitlendi, eylemi sahneye göre değişti.
- Sahne üretimi `tools/make_samples.py` ile yeniden çalıştırılabilir.

**P2 — Türkçe etiketleri ayrı katmana taşıma**

- JSON etiketi, TrueType/OpenType glif denetimi, sınır/çakışma denetimi, alfa metin PNG, metin SVG ve SHA-256 manifest eklendi.
- `tools/render_turkish_labels.py` tek komutla temel PNG + etiket JSON'unu birleştirir.
- SKILL ana akışına yazısız temel sahne ve sonradan eklenen Türkçe katman ilkesi yerleştirildi.
- Otomatik kabul testleri ve P1/P2 kullanım rehberi eklendi.

**Sınırlar:** OCR yapılmaz; sahne nesneleri ile etiket çakışması, semantik doğruluk ve üretici modelde karakter benzerliği garantisi otomatik sağlanmaz. Türkçe font paket içinde dağıtılmaz. P3 teknik diyagram motoru ve P4 genel SVG düzenleme yapılmadı. GitHub'a push yapılmadı.
