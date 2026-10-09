# P3 — Teknik çizim örnekleri

Dört **temsili**, kullanıcı projesine ait olmayan test veri kümesidir:

| Dosya | Şablon | Anlamsal amaç |
|---|---|---|
| `01-yazilim-mimarisi.json` | architecture | UI → API → İş Mantığı → Veritabanı (+ Harici Servis) |
| `02-veri-akisi.json` | data-flow | Ham veri → Temizleme → Doğrulama → Rapor |
| `03-ml-pipeline.json` | ml-pipeline | Eğitim/veri ve tahmin yollarını ayrı göstermek |
| `04-muhendislik-sistemi.json` | engineering-system | Sensör → Denetleyici → Eyleyici → Sistem ve geri besleme |

JSON şeması için `minimaladam/references/technical-mode.md` dosyasını oku.

Bunlar gerçek bir projenin çıkarılmış mimarileri değil, motorun test örnekleridir.

```bash
python -m pip install -r requirements.txt
python tools/render_technical_diagram.py --spec examples/technical/specs/04-muhendislik-sistemi.json --output-dir examples/technical/generated
python -m unittest discover -s tests -v
```

Not: SVG'deki `<text>` öğeleri font ailesi ismiyle tanımlanır; fontu başka bir makinede yoksa yerleşim değişebilir. PNG çıktısı üretildiği ortamda rasterleştirilmiştir. SVG kaynağına yeni veri ekleyerek şemanın kanıtlanmış mimari olduğu sonucuna varılamaz.
