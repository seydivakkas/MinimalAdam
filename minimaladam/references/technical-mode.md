# P3 — Teknik Çizim Modu (Kaynak Tanımlı SVG Şema)

## Kapsam

Bu mod, P1/P2'nin serbest kavram illüstrasyonu moduna **alternatiftir**. Kullanıcı yazılım mimarisi, veri akışı, model eğitimi veya mühendislik denetimi için **teknik ve yönlü ilişkilerin doğruluğunu** istediğinde uygula. Sade beyaz zemin, siyah ince hat, az renk, Türkçe metin ve işin içinde olan MinimalAdam korunur. Teknik modda kutu/ok kullanımı izinlidir; genel illüstrasyon modundaki “resmi şema yapma” yasağı yalnız genel mod içindir.

**Gerçek projeyi uydurma:** Depo, kod, mimari tanımı veya belgede bulunmayan servis, veritabanı, model, işlev, fiziki bağlantı ya da etiket ekleme. Kullanıcının verileri eksikse veri iste veya örneği "temsili" diye açıkça belirt. Görsel üreterek sistemin doğruluğu kanıtlanmaz.

## Desteklenen dört mod

- `architecture`: istemci/servis/veri saklama gibi yazılım bileşenleri ve yönlü bağlantılar.
- `data-flow`: girdiden çıktıya dönüştürme hattı, filtre, kontrol, son çıktı.
- `ml-pipeline`: eğitim ve inference ayrımı; eğitim çıktısının tahmine aktarılması.
- `engineering-system`: sensör, denetleyici, eyleyici, fiziksel süreç ve gerçek geri besleme.

Her resim **tek odak** taşır. Bir resme en fazla 8 düğüm, 12 ilişki koy. Daha fazlasını birkaç bağımsız sahneye böl.

## Teknik bilgi şeması

Girdi UTF-8 JSON'dur, **piksel koordinatları değil 0..1 oranları** kullanılır. `version=1`, `mode`, `concept`, `nodes`, `edges`, `minimaladam` zorunludur. `nodes` içinde `id`, kısa `label`, `kind`, `x`, `y`, tercihen `w`/`h` bulunur. `edges` içinde gerçek `from`/`to`, `kind`, isteğe bağlı `from_port`,`to_port`,`via`,`label` bulunur. `via` bir dizi `[x,y]` ara koordinatıdır. `minimaladam` içinde `x`,`y`,`action`,`edge` bulunur; `edge`, karakterin eliyle temasta olması gereken bağlantının **sıfır tabanlı indeksi**dir.

**Yasal node kind:** `client`, `process`, `service`, `data`, `model`, `sensor`, `actuator`, `system`, `result`.

**Yasal edge kind ve görsel kuralları:**

| Bağlantı | Anlam | Gösterim |
|---|---|---|
| `data` | Veri taşınması | Turuncu düz ok |
| `control` | Komut/yönetim | Siyah düz ok |
| `feedback` | Geri besleme | Mavi kesik ok |
| `physical` | Fiziksel etki | Kırmızı noktalı ok |

Bu görsel sözlük *bağlantı semantiği* içindir. Teknik şemayı sadece renklerle okuyabilme zorunluluğu yoktur; stroke türleri de ayrılır. Renkleri başka nesnel anlamlar için yeniden kullanma.

## Örnek kullanım

Depo kökünde:

```bash
python -m pip install -r requirements.txt
python tools/render_technical_diagram.py \
  --spec examples/technical/specs/03-ml-pipeline.json \
  --output-dir examples/technical/generated
```

Kurulu Codex Skill içinden (Windows'ta `python` mevcutsa):

```powershell
python "$HOME\.codex\skills\minimaladam\scripts\render_technical_diagram.py" `
  --spec "$HOME\.codex\skills\minimaladam\examples\technical\03-ml-pipeline.json" `
  --output-dir ".\outputs\ml-teknik"
```

## Çıktılar ve garanti düzeyi

- `*.base.svg`: vektör çizgi, ikon, karakter; **etiket bulunmaz**.
- `*.labels.svg`: Türkçe **vektör metin** katmanı; saydam arka plan.
- `*.svg`: grup kimlikleriyle birleşik SVG. Metin SVG `<text>` olarak kalır (vektör düzenleyicide düzenlenebilir, font sistemde yüklü olmalıdır).
- `*.png`: 1600×900 çözünürlükte birleşik çıktı.
- `*.manifest.json`: kaynak JSON SHA-256, font SHA-256, çıktı SHA-256 ve QA alanları.

Kontroller: geçersiz kaynağı/bağlantıyı, yinelenen ilişkiyi, kayıp Türkçe glifi, Unicode NFC ihlalini, aşırı uzun etiketi, düğüm çakışmasını, üçüncü düğümü delen oku, etiketler arası çakışmayı, kadraj taşmasını ve MinimalAdam'ın bağlama uzak olmasını reddeder. **Sınırlar:** her olası ok-ok kesişimi, görseli etkileyen bütün çapraz noktalar, figür-metne teması, sistemin semantik doğruluğu veya gerçek mühendislik fizibilitesi otomatik kanıtlanmaz. Özellikle geri besleme ve fiziksel bağlantıları kaynak belgeye göre manuel incele.

## Sürüm sınırlaması

P3, doğrudan düzenlenebilir SVG **dosyaları** üretir; tam bir GUI SVG editörü, otomatik graph layout, CAD/BIM doğrulama, simülasyon, kaynak koda otomatik mimari keşif veya bütün SVG çizim nesnelerini JSON'a geri senkronlayan bir editör içermez. Bu gelişmiş fonksiyonlar P4+ kapsamındadır.
