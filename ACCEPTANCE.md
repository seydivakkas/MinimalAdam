# MinimalAdam — Kabul ve Yayın Kanıtları (P6)

Bu belge **gözlemlenen otomatik test kanıtını**, **kullanıcı tarafından yapılan Windows kabulünü** ve **henüz doğrulanmayan kapsamı** birbirinden ayırır.

## A. GitHub Actions — PASS (bağımsız CI kanıtı)

- Kod dalı: `main`, commit `502a824b65b051284b8f86be77830ed0d91ec213`.
- Windows Actions: [Windows acceptance #4](https://github.com/seydivakkas/MinimalAdam/actions/runs/37998204445) — **completed / success**.
- Python 3.12 (Windows): **40/40 Python**, **22/22 JavaScript**, P4/P5 Chromium E2E ve paket doğrulamaları **PASS**.
- Python 3.14 (Windows): aynı kabul aşamaları **PASS**.
- Önceki hatalar düzeltildi: Windows CRLF/LF kaynak SHA-256 uyuşmazlığı (PR #1); Windows konsolunda `cp1252` Türkçe `ğ` yazdırma hatası (`PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1`).
- PR kanıtı: [#1](https://github.com/seydivakkas/MinimalAdam/pull/1), merge commit `502a824b65b051284b8f86be77830ed0d91ec213`.

## B. Windows masaüstü kullanıcı kabulü — PASS (kullanıcı beyanı)

**2026-10-10:** Kullanıcı, GitHub'daki güncel MinimalAdam sürümüyle aşağıdaki altı denemenin hepsinin çalıştığını bildirdi:

| No | Manuel kabul adımı | Durum | Kanıt türü |
|---|---|---|---|
| 1 | `MinimalAdam-Studio.cmd` ile editörün açılması ve örnek çizimin görünmesi | PASS | Kullanıcı beyanı |
| 2 | Düğümün fare ile taşınması | PASS | Kullanıcı beyanı |
| 3 | Türkçe düğüm etiketinin değiştirilmesi | PASS | Kullanıcı beyanı |
| 4 | SVG olarak dışa aktarım | PASS | Kullanıcı beyanı |
| 5 | PNG olarak dışa aktarım | PASS | Kullanıcı beyanı |
| 6 | JSON kaydetme ve aynı projeyi yeniden açma | PASS | Kullanıcı beyanı |

Bu adımların tümü **kullanıcı tarafından doğrulanmıştır**; ekran kaydı veya bu kullanıcının Windows cihazından bağımsız otomatik log alınmamıştır. GitHub Actions tarayıcı E2E kayıtları aynı işlevleri ek olarak otomatik test eder; bu iki kanıt türü birbirinin yerine kullanılmaz.

## C. Paket kapsamı ve sınırlar

- **Doğrulandı:** Windows CI P1–P5 (Python 3.12 / 3.14); temel editör masaüstü kullanım kabulü; SVG/PNG/JSON işlemleri.
- **Doğrulanmadı:** Gerçek Codex ajan ortamındaki bütün uçtan uca işlevler; farklı donanım/font kombinasyonları; görsel estetik ve semantik mimari doğruluk; çok düğümlü geniş ölçekli grafiklerin performansı.
- Örnek teknik diyagramlar **temsili** içeriktir; gerçek sistemlerin doğrulanmış mimarisi değildir.
- Özgün yazılımın MIT lisansı ve Ian'a ait karakter/görsel dilinin atfı `LICENSE` ve `NOTICE.md` içinde korunur.

## D. Yayın durumu

- GitHub kaynak deposu: https://github.com/seydivakkas/MinimalAdam — **PUSH DOĞRULANDI**.
- GitHub Actions Windows: **PASS** (üstteki çalışma).
- GitHub Release: **henüz yayımlandığı doğrulanmadı**. Yayın için sürüm etiketi, kaynak paketi, sürüm notları ve son kanıt kontrolü gerekir.
- Sonraki sürüm notları taslağı: [docs/RELEASE_NOTES_v0.6.1.md](docs/RELEASE_NOTES_v0.6.1.md).
