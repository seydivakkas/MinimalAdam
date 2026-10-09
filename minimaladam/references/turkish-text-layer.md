# P2 — Ayrı Türkçe Yazı Katmanı

## Amaç ve sınır

Görsel modeli Türkçe kelimeleri çizim piksellerine yazmak yerine **yazısız** sahne üretir. Etiketler UTF-8 JSON dosyasında doğrulanır; `tools/render_turkish_labels.py` seçili TrueType/OpenType fontun gerçek Unicode glif haritasını inceleyip şeffaf PNG katmanına yazar ve sahne üzerine birleştirir.

Bu yöntem **girdi metnindeki karakterleri korur** ve programatik glif/yerleşim kontrolü yapar. Sözcüğün anlamca doğru olup olmadığını veya metnin çizim objeleriyle çakışmadığını otomatik olarak doğrulamaz. Yazılar doğrudan PNG içine üretiliyorsa o alanlar bu yöntemle güvenilir biçimde temizlenemez. Yazısız temel görsel şarttır.

## Tek görsel için uygulama

1. Konu, eylem, kompozisyonu belirle; MinimalAdam görselde bir işi fiilen yapsın.
2. Görsel modeline: **"Görselin hiçbir yerinde harf, sayı, başlık, logo, tabela, kod veya okunabilir işaret üretme. Metinler sonradan ayrı katmanda eklenecek."** talimatını ver.
3. 16:9 yazısız PNG'yi `ornek.base.png` olarak kaydet.
4. Etiketleri `ornek.labels.json` içine yaz. Her etiket yalnızca `text`, `x`, `y`, isteğe bağlı `color`, `size`, `anchor` alanlarını kullanır.
5. Yazı katmanını ayrı oluştur, görünürlük/çakışma kontrolünden geçir.

```bash
python tools/render_turkish_labels.py --base ornek.base.png --labels ornek.labels.json --output ornek.png
```

Windows PowerShell:

```powershell
py -3 tools/render_turkish_labels.py --base .\ornek.base.png --labels .\ornek.labels.json --output .\ornek.png
```

Paket kökünde `pip install -r requirements.txt` gereklidir. Varsayılan Windows Segoe UI ve Linux DejaVu Sans gibi sistem fontları aranır. Alternatif bir Türkçe destekli font için `--font C:\...\font.ttf` kullan. **Font dosyaları pakette dağıtılmaz.**

## JSON etiket şeması

```json
{
  "version": 1,
  "labels": [
    { "text": "Dağınık bilgi", "x": 0.275, "y": 0.305, "color": "black", "size": 40, "anchor": "center" },
    { "text": "Süzgeç", "x": 0.50, "y": 0.305, "color": "blue", "size": 40 },
    { "text": "Net fikir", "x": 0.70, "y": 0.305, "color": "black", "size": 40 }
  ]
}
```

`x,y` koordinatları 0–1 aralığındadır; (0,0) sol üst köşe. `size`, 1600 piksel genişlikte kullanılan piksel birimidir; daha büyük 16:9 görsellerde orantılı ölçeklenir. `anchor` = `left | center | right`; renkler `black | red | orange | blue` ile sınırlıdır.

Kontroller: 8 etiketten fazla yok, her etiket 1–24 karakter ve tek satır, Unicode NFC, Çince veya bozuk karakter yok, fontta eksik glif yok, görsel 16:9, etiketler taşmıyor veya birbirleriyle çakışmıyor. Bu kısıtların bilinçli olarak ihlali hata üretir; sözcükleri otomatik değiştirmez.

## Çıktılar

- `ornek.png`: birleşik nihai PNG
- `ornek.text.png`: şeffaf **metin katmanı**; temel sahneye geri uygulanabilir
- `ornek.labels.svg`: sadece SVG metin katmanı. **Tam sahnenin vektörel karşılığı değildir** ve farklı sistem fontuyla farklı ölçülebilir.
- `ornek.manifest.json`: etiket listesi, boyut, glif ve çakışma kontrolleri, temel görsel/font/etiket SHA-256 değerleri

## Geçerli pratik

Önce görünür etiketi JSON'da düzelt, sonra katmanı **sıfırdan yeniden üret**. PNG üzerindeki bozuk yazıya ikinci bir yazı yapıştırma. `--font` ile sistem fontunu bilinçli seç; otomatik varsayılan font dizini hedef bilgisayarda değişebilir. Türkçe karakterlerin çizimi gerçek font gliflerinden gelir, görüntü modeli tahmin etmez.

## P1 örnekler

`examples/specs/` içinde aynı MinimalAdam gövde sembolünden üretilmiş üç özgün **yazısız SVG** ve etiket JSON'ları bulunur. `examples/generated/` içinde temel PNG, şeffaf yazı katmanı, nihai PNG, SVG yazı katmanı ve manifest bulunur.

Tekrar üretim:

```bash
python tools/make_samples.py
```

Örnek SVG sahneleri P1 test fikstürleridir; bütün görüntü modelleri için otomatik karakter tutarlılığı garantisi değildir. Otomatik görüntüsel benzerlik ölçümü ayrıca geliştirilmelidir.
