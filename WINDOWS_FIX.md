# Windows Python 3.14 — Cairo DLL hatası düzeltmesi (v0.6.1)

## Görülen hata

`OSError: no library called "cairo-2" was found` / `libcairo-2.dll`.

Bu, `pip install CairoSVG` komutu başarılı olsa bile Windows'ta Cairo yerel DLL'i bulunamadığında meydana gelir. v0.6.0, P3 teknik şemayı PNG'ye çevirmek için CairoSVG'yi koşulsuz çağırıyordu.

## Kalıcı düzeltme

- v0.6.1 normal **P3 SVG + PNG üretiminde yalnız Pillow** kullanır; GTK/Cairo DLL'i aranmaz.
- SVG, ayrı etiketler, manifest ve kaynak JSON şeması korunur.
- SVG ile PNG aynı şema verisinden oluşturulur. Raster sonucu fontlara ve platforma göre görsel olarak küçük farklılıklar gösterebilir.
- Yeni test, Python ortamında `cairosvg` ve `cairocffi` tamamen yokmuş gibi çalışarak yine 1600×900 PNG üretildiğini doğrular.
- CI, Windows Python **3.12 ve 3.14** matrisiyle çalışır.

Önemli: Eski `tools/make_samples.py`, yalnız P1 orijinal SVG kaynak örneklerini yeniden üretmek isteyen geliştiriciler için isteğe bağlı CairoSVG kullanmaya devam eder. v0.6.1 ZIP içerisinde zaten hazır P1 sahneleri vardır. Normal kullanım, test, yayın ve P3 şema üretimi `make_samples.py` çalıştırmaz.

## Yeni yayın denemesi

1. `MinimalAdam-v0.6.1.zip` arşivini eski v0.6.0 klasörünün **dışında yeni bir klasöre** çıkar.
2. Yeni pakette `Publish-MinimalAdam.cmd` dosyasına çift tıkla.
3. Başarılı olursa [GitHub deposunda](https://github.com/seydivakkas/MinimalAdam) `Actions > Windows acceptance` iş akışının Python 3.12 ve 3.14 işlerini kontrol et.

`pip uninstall CairoSVG` veya GTK yüklemesi gerekmez.

## Kabul kanıtı sınırı

Linux üzerinde Python 40/40, JavaScript 22/22, P4 ve P5 Chromium E2E, üç statik kontrol başarılı. **Kullanıcının Windows makinesinde v0.6.1 yeniden denenene ve GitHub Windows CI çalışana kadar Windows PASS denemez.**
