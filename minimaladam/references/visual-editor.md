# P4 — MinimalAdam Studio (yerel görsel editör)

## Amaç

P3 JSON v1 şemalarını elle düzenleyen, Türkçe etiketli, tamamen yerel çalışan HTML/SVG editör. **Yeni mimariyi kendi kendine çıkarmaz.** JSON'daki node/edge'leri gösterir ve kullanıcının onaylı değişikliklerini veriye yansıtır.

## Açılış

- Windows: ZIP açıldıktan sonra kökteki `MinimalAdam-Studio.cmd` dosyasına çift tıkla.
- Her platform: `editor/offline.html` dosyasını Chrome/Edge/Firefox ile aç. Tek dosyalık sürümde sunucu gerekmez.
- Geliştirici sürümü: `python tools/start_studio.py` (yalnızca `127.0.0.1:8765`), ardından `http://127.0.0.1:8765/`.
- Codex Skill klasöründen: `editor/offline.html` dosyasını aç.

## İşlevler

1. P3 JSON kaynak dosyası veya P4 `.project.json` yükle. Dört örnek yerleşiktir.
2. Düğümü sürükle, seçip Türkçe etiketini, türünü, vurgu rengini, boyutunu veya sayısal konumunu değiştir.
3. Bağlantı kur aracıyla kaynak ve hedefe sırayla tıkla. Bağlantı seçildikten sonra yönünü, türünü, etiketini, bağlantı portlarını ve `via` ara noktalarını düzenle.
4. MinimalAdam'ı seç: eylem, bağlı kenar, ölçek; bağlantıya hizala.
5. Üç görünüm: **el çizimi**, **teknik**, **kontrast**. Düzenlenen grafik verisi aynı kalır.
6. Ctrl+Z/Ctrl+Shift+Z ile geri al/ileri al. Proje sürümleri otomatik kaydedilmez: kapatmadan önce JSON indir.
7. Projeyi `*.project.json` ile tam stil + şema olarak, P3 Python motoruna uygun şemayı `*.json` olarak indir.
8. PNG 1600×900 ve SVG indir. **P4'ün SVG çıktısı gömülü `minimaladam-editable-spec` metadata içerir ve aynı editörde tam verisiyle tekrar açılabilir.**

## Eski P3 SVG dosyalarını açma

P3 v0.3'ün SVG'leri tam grafik kaynak kodunu ve tüm semantik metadata'yı taşımaz. Editör tanınabilen P3 düğümleri ve uç geometrisinden sınırlı yeniden kurma yapabilir. **Mod ve MinimalAdam eylemi kesin olarak geri kazanılamaz.** Eski SVG açılsa bile şemayı özgün P3 JSON ile karşılaştır; uyarı görülecektir. Belirsiz uçları veya karakteri güvenle eşleyemediğinde SVG açmayı reddeder. P3 JSON daima asıl kayıt kaynağıdır.

## Tasarım / güvenlik sınırları

- Görsel editör internet, bulut, API anahtarı, Node veya Python gerektirmez. Yalnız modern tarayıcı ve yerel sistem fontu kullanır.
- Otomatik graf yerleşimi, kapsamlı oto-routing ve karmaşık polylinelerin manuel tuval tutamakları henüz yok. `via` noktaları alanından düzenlenir.
- P3 2–8 düğüm, 1–12 bağlantı, 1600×900 koordinatlarını temel alır. P4 kısıtlarla ilgili uyarılar gösterir; P3 Python motoru daha katı doğrulama yapabilir.
- Sahne çizimi **CAD, elektronik simülasyon, UML sözdizimi doğrulayıcı veya gerçek ML eğitim hattı değildir**. Geometri ve etiket kalitesi testleri gerçek sistem doğruluğunu garantilemez.
- SVG veya JSON içe aktarımı için script çalıştırılmaz; yalnız beklenen şema ve sınırlı P3 SVG yapısı işlenir. SVG dışa aktarılan metin XML olarak kaçışlanır.
- Dosyalar kullanıcının tarayıcısında işlenir; arka planda sunucuya gönderilmez.

## Test

```powershell
node --test tests/js/p4_core.test.mjs
python tests/e2e_p4.py  # Chromium + Playwright bulunan geliştirme ortamında
python -m unittest discover -s tests -p "test_*.py" -v
```

E2E testi yerel HTML, CSS, JS içeriğini Chromium'a enjekte ederek etkileşimleri kontrol eder; gerçek işletim sistemi tarayıcı kurulumunun tüm varyantlarını temsil etmez.
