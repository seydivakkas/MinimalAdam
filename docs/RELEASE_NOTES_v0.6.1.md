# MinimalAdam v0.6.1 — İlk Windows kabulü tamamlanan sürüm

MinimalAdam, Türkçe illüstrasyon yönergelerini, ayrı Türkçe yazı katmanını ve teknik şemalar için çevrimdışı çalışan görsel editörü bir araya getirir.

## Öne çıkan özellikler

- **P1:** MinimalAdam karakterinin ortak görsel diliyle üç Türkçe örnek illüstrasyon.
- **P2:** Türkçe etiketlerin JSON üzerinden gerçek fontlarla ayrı işlenmesi; şeffaf metin katmanı.
- **P3:** Mimari, veri akışı, ML pipeline ve mühendislik sistemi için kaynak tanımlı JSON → SVG/PNG üretimi.
- **P4:** Bağımsız çevrimdışı HTML editör; düğüm taşıma, etiket/bağlantı düzenleme, geri al/ileri al, üç stil, SVG/PNG dışa aktarım ve JSON proje kaydı.
- **P5:** Açıklanabilir PASS/REVIEW/FAIL kalite kapısı; sınır, etiket, bağlantı, karakter konumu ve raster kalite kontrolleri.

## Windows kurulumu

1. GitHub Release varlıklarından veya GitHub `Code → Download ZIP` seçeneğinden kaynak paketini indir.
2. ZIP dosyasını çıkart (ZIP arşivinin içinden çalıştırma).
3. `MinimalAdam-Studio.cmd` dosyasına çift tıkla. Alternatif: `editor/offline.html` dosyasını Edge veya Chrome'da aç.
4. Örnek şema üzerinde değişiklik yap ve JSON/SVG/PNG dışa aktar.

**Editörü kullanmak için Python, Node.js, ücretli API veya internet gerekmez.** Python ve Node.js test/geliştirme araçları içindir.

## Düzeltmeler

- Windows Python 3.14 üzerinde eksik Cairo DLL'den kaynaklanan PNG üretim hatası giderildi: P3 PNG, CairoSVG yerine Pillow kullanır.
- Windows Git checkout'ta JSON/SVG satır sonları için LF zorunlu kılındı; dosya özeti kontrolü gevşetilmedi.
- GitHub Actions Windows konsolundaki `cp1252` Türkçe karakter çıktısı UTF-8 ile düzeltildi.

## Doğrulama ve kanıt

- [Windows CI: Python 3.12 ve 3.14 PASS](https://github.com/seydivakkas/MinimalAdam/actions/runs/37998204445) — iki işte 40 Python testi, 22 JS testi, P4/P5 Chromium E2E ve statik paket denetimleri.
- Windows masaüstü kullanıcı kabulü: editörün açılması, düğüm taşıma, Türkçe etiket değişikliği, SVG/PNG dışa aktarma ve JSON yeniden açma; altı adımın tamamı **kullanıcı tarafından başarılı bildirildi**.
- Ayrıntı: [ACCEPTANCE.md](../ACCEPTANCE.md).

## Kapsam sınırları

Bu sürüm bağımsız bir AI görüntü modeli içermez. Teknik şemalar, tanımlanmış düğüm ve bağlantılara dayanır; otomatik CAD/simülasyon, genel amaçlı SVG editörü, gerçek sistemin doğruluğunu kanıtlama veya karmaşık otomatik yerleşim iddiası yoktur. Codex ajanı uçtan uca kabulü henüz bağımsız doğrulanmadı.

Özgün [Ian Xiaohei Illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations) çalışmasına ve Ian'a atıf korunmuştur; MIT lisansı için [LICENSE](../LICENSE) ve [NOTICE.md](../NOTICE.md) dosyalarına bakın.

## Sürüm paketinin bütünlüğünü doğrulama

Bu sürümde üç indirme varlığı bulunur:

- `MinimalAdam-v0.6.1.zip` — çevrimdışı editör, Codex Skill, örnekler, kaynak ve testler.
- `MinimalAdam-v0.6.1.manifest.json` — kaynak commit'i ve paket içindeki her dosyanın SHA-256 özeti.
- `SHA256SUMS.txt` — ZIP ve manifest varlıklarının SHA-256 özetleri.

Dosyaları aynı klasöre indirdikten sonra Windows PowerShell'de:

```powershell
Get-FileHash .\\MinimalAdam-v0.6.1.zip -Algorithm SHA256
Get-FileHash .\\MinimalAdam-v0.6.1.manifest.json -Algorithm SHA256
Get-Content .\\SHA256SUMS.txt
```

Komutlardan gelen SHA-256 değerlerini `SHA256SUMS.txt` içindeki karşılıklarıyla eşleştirin. Release, yalnızca `main` dalında başarılı Windows CI doğrulamasından sonra yayımlanır. Bağımsız doğrulama kayıtları [ACCEPTANCE.md](https://github.com/seydivakkas/MinimalAdam/blob/main/ACCEPTANCE.md) dosyasındadır.
