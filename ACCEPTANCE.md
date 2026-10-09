# MinimalAdam v0.6 — Kabul Testi Kanıtları

## Bu ortamda doğrulananlar (Linux / Chromium)

- Python `unittest`: **40/40 PASS**.
- JavaScript `node --test`: **22/22 PASS**.
- P4 tarayıcı E2E: **PASS** (sürükle/bırak, Türkçe etiketler, geri al, stiller, P3/P4 JSON, PNG 1600×900, SVG round-trip, bağlantılar).
- P5 tarayıcı E2E: **PASS** (uyarı, dışa aktarma engeli, onay, onayın proje değişince sıfırlanması).
- P3 örnekleri: dört declarative JSON girdisinden SVG/PNG/manifest yeniden üretimi; SHA-256 içerik kontrolleri.
- Paket statik denetleyicileri: `validate-package.py`, `validate_p4.py`, `validate_p5.py` PASS.
- Önceki `xiaohei` JSON karakter alanı ve `xiaohei-editor-v1` proje kimliği: geriye uyumlu dönüşüm testi PASS.

## Henüz doğrulanmayanlar

- **Windows üzerinde gerçek çalıştırma: NOT_RUN.** Windows CI tanımı var, ancak GitHub'a gönderilmeden workflow çalışmaz.
- **GitHub push: NOT_DONE.** https://github.com/seydivakkas/MinimalAdam deposu oluşturuldu ve yazma erişimi doğrulandı; dosyaların tam kaynak kod hâlinde `main` dalına gönderilmesi bekleniyor. `Publish-MinimalAdam.cmd` ve `tools/publish-github.ps1` bunu Git for Windows kimlik doğrulamasıyla gerçekleştirir.
- Gerçek Codex çalışma zamanı kabulü: NOT_RUN.
- Farklı Windows fontlarının çizim estetiği: NOT_VERIFIED. CairoSVG, P3 için artık zorunlu değil.
- 2026-10-10: kullanıcıda v0.6.0 / Windows Python 3.14 ile `cairo-2.dll` bulunamadı; P3 testi başarısız kaldı. v0.6.1 Pillow düzeltmesinin gerçek Windows kabulü henüz bekleniyor.
- Görsel estetik, mimari gerçeklik ve anlamsal uygunluk: NOT_VERIFIED.

GitHub Actions sonuçlarının başarılı olduğu **ancak iş akışı çalışıp kanıt üretildikten sonra** ilan edilmesi gerekir.
