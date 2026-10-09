---
name: minimaladam
description: Türkçe makale, blog, gönderi, Notion belgesi, metodoloji, süreç, yapı, durum ve kavramlar için MinimalAdam tarzında beyaz zeminli, el çizimi, sıra dışı ve sade 16:9 illüstrasyonlar planla, üret veya düzenle. Türkçe kısa etiketler, küçük siyah MinimalAdam karakteri ve sınırlı kırmızı/turuncu/mavi vurgu kullan. Görsel planı, çizim listesi (shot list) ve görseldeki hatalı yazıları düzeltme isteklerinde uygulanır.
---

# MinimalAdam — Türkçe Görsel Anlatım Skill’i

> Kaynak: https://github.com/helloianneo/ian-xiaohei-illustrations
> Özgün kaynak Ian Xiaohei Illustrations (Ian); MinimalAdam ayrı bir türev projedir. Atıf ve lisans için NOTICE.md dosyasına bak.

## Temel amaç

Türkçe metinlerdeki önemli bir yargıyı, süreci, yapıyı, durumu veya mecazı, akılda kalıcı **16:9 yatay** bir el çizimiyle anlat. Bu çalışma ticari illüstrasyon veya sevimli maskot tasarımı değildir. **P3/P4 teknik mod** istisnasında kaynak tanımlı, şematik teknik mimari üretimi desteklenir; serbest illüstrasyon kısıtlarını buna zorla uygulama.

Varsayılan karakter **MinimalAdam**: siyah dolu gövde, iki beyaz nokta göz, ince bacaklar, ifadesiz ve ciddi yüz. MinimalAdam, görselin ana kavramsal eylemini bizzat gerçekleştirir; köşede dekor olarak durmaz.

**Dil kuralı:** Kullanıcı başka bir dil istemedikçe açıklamalar, çizim listeleri, son kullanıcıya gösterilen tüm etiketler ve çizim üzerindeki okunabilir yazılar **Türkçe** olsun. Teknik terim gerektiğinde Türkçe karşılıkla kullan; özel adları, kod ve dosya isimlerini çevirme. Türkçe karakterleri (ç, ğ, ı, İ, ö, ş, ü) doğru yaz. Çizimde Çince veya İngilizce açıklama bırakma; yalnızca kullanıcı özellikle istediğinde kullan.

## İhtiyaca göre okunacak referanslar

- `references/style-dna.md`: Görsel kimlik, renk, tipografi ve yasaklar.
- `references/minimaladam-character.md`: Karakterin görünümü, eylemleri ve sınırları.
- `references/composition-patterns.md`: Kompozisyon türleri ve özgün mecaz geliştirme yöntemi.
- `references/prompt-template.md`: Tek görsellik üretim ve düzenleme istemleri.
- `references/qa-checklist.md`: Üretim sonrası kalite denetimi.
- `references/turkish-text-layer.md`: Yazısız sahne + kesin Türkçe glif/etiket katmanı ve birleştirme komutları.
- `references/technical-mode.md`: P3 mod seçimi, deklaratif JSON şeması, 4 örnek, SVG/PNG üretimi ve doğruluk sınırları.
- `references/visual-editor.md`: P4 offline HTML editör, sürükle-bırak, bağlantı/etiket düzenleme, JSON/SVG/PNG ve testler.
- `editor/offline.html`: Kod ve CSS içeren tek dosyalık, internetsiz çalışan P4 editörü.
- `scripts/render_technical_diagram.py` ve `scripts/render_turkish_labels.py`: kurulumdan sonra Skill içinde doğrudan kullanılabilen P3/P2 araçları.
- `examples/technical/`: dört temsili teknik girdi JSON dosyası.
- `assets/examples/`: P1 kapsamında üretilmiş üç özgün Türkçe sahne örneği; örnekleri doğrudan kopyalama. Özgün Ian ikili görselleri pakete eklenmemiştir.

Tüm referansları gereksiz yere aynı anda bağlama yükleme.

## Dört üretim yolu

1. **Serbest kavram illüstrasyonu (P1/P2):** Aşağıdaki standart iş akışını izle; teknik doğruluk iddiasında bulunma.
2. **Teknik şema (P3):** Kullanıcı yazılım mimarisi, ML pipeline, veri akışı, geri beslemeli denetim veya benzer somut bileşen ilişkileri istiyorsa `references/technical-mode.md` dosyasını oku. İlk önce kaynakta kanıtlanan node/edge listesini çıkar; gerçek sistem kaynağı yoksa şemayı açıkça **temsili** yap veya kullanıcıdan eksik bağlantıları iste. UTF-8 JSON şemasını hazırlayıp `scripts/render_technical_diagram.py` aracını çalıştır. **SVG + PNG + katman SVG + manifest** dosyalarını birlikte teslim et. Dokümana dayanmayan bağlantıları ekleme. Teknik modda kutu/ok çizmek yasak değildir, ama her görsel sade ve kolay okunur olmalı.

3. **Teknik şema editörü (P4/P5):** Kullanıcı mevcut teknik grafik üzerinde elle düzenleme istiyorsa `references/visual-editor.md` rehberini kullan. `editor/offline.html` dosyasını sunabilir; P3 JSON ve P4 proje dosyalarıyla düğüm, bağlantı ve kısa Türkçe etiketler düzenlenebilir. SVG içine P4 metadata gömülür; P3 eski SVG importu yaklaşık olup kontrol ister. Harici API veya bulut gerekmez.

4. **P5 Kalite Kapısı:** Kaynak tanımlı teknik şema her düzenlemeden sonra `references/quality-gate.md` kurallarıyla denetlenir. `FAIL` durumunda teslimi durdur; `REVIEW` uyarılarını raporla ve kullanıcı açıkça onaylamadan dışa aktarma. PNG çıktısını `scripts/inspect_render.py` ile ölç. `PASS`, estetik veya anlam doğruluğu değildir. Teknik şemaya ait özgün kaynak JSON ve QA raporunu sakla. Serbest illüstrasyonlarda yalnız PNG raster QA ve insan kontrollü nitelik değerlendirmesi kullanılabilir.

## Çalışma akışı

### 1. Metni anla

Kullanıcının metnini, bağlantısını, Markdown/Notion içeriğini veya ekran görüntüsünü incele. Şunları ayırt et:

- Ana tez veya temel düşünce.
- Anlamın değiştiği veya kararın verildiği kritik noktalar.
- Görsel anlatıma uygun bölümler.
- Yalnızca yazıyla anlatılması daha doğru olan bölümler.

Her paragrafa resim ekleme. Öncelik: merkezi iddia, darboğaz, giriş-işleme-çıkış döngüsü, ayrıştırma, öncesi-sonrası karşılaştırma, tekrarlanan kullanım, kullanıcı yolu, sık hata ve durum değişimi.

### 2. Önce görsel stratejiyi oluştur

Kullanıcı yalnızca analiz veya öneri istiyorsa resim üretme. **Çizim listesi (shot list)** ver; her çizim için:

1. Hangi paragrafın veya bölümün sonuna yerleşeceği.
2. Konu.
3. Tek cümlelik ana fikir.
4. Kompozisyon türü.
5. MinimalAdam'ın gerçekleştireceği eylem.
6. Kullanılacak temel nesneler.
7. Önerilen **Türkçe**, kısa etiketler.

Varsayılan olarak 4–8 görsel öner; kısa metinler için 1–3, uzun metinler için normalde en çok 9. Gereksiz çizim ekleme.

### 3. Önce yazısız görseli üret, sonra ayrı Türkçe etiket katmanını oluştur

Kullanıcı açıkça üretim istiyorsa ve ortamda görüntü üretimi mevcutsa her görseli **ayrı ayrı** üret. Üretim aracı yoksa üretmiş gibi davranma; uygulanabilir istemleri teslim et. Birden fazla çizimi tek tuvale sıkıştırma. **P2 varsayılanı: görüntü modelinden üzerinde hiçbir yazı, sayı, sahte harf veya başlık bulunmayan temel sahne iste.** Türkçe etiketleri ayrıca JSON içinde oluştur ve yazı katmanı aracıyla ekle.

Her çizimin isteminde şunlar bulunsun:

- 16:9 yatay oran.
- Tam beyaz, dokusuz zemin.
- İnce, hafif düzensiz siyah el çizimi çizgiler.
- Bol boş alan.
- Yalnızca gerekli yerlerde kırmızı/turuncu/mavi vurgu.
- JSON içinde en çok 8, tercihen 3–5 kısa **Türkçe** etiket (görsel modelinin çizimin içine yazması yasaktır).
- Merkezi kavramsal işi MinimalAdam'ın yapması.
- PPT görünümü, çocuk çizimi, yoğun akış şeması, karmaşık arka plan ve gereksiz başlık bulunmaması.

Önceki örneklerin fiziksel nesnelerini veya kompozisyonlarını varsayılan olarak yeniden kullanma. Güncel metne özgü yeni bir mecaz icat et.

### 4. Ayrı Türkçe yazı katmanını uygula

Görsel üretildikten sonra `references/turkish-text-layer.md` içindeki `render_turkish_labels.py` aracıyla 16:9 yazısız PNG + UTF-8 JSON etiketlerini birleştir. Fontta Türkçe glif bulunmazsa, etiket başka etikete çarparsa veya kadraj dışına taşarsa **teslim etme; hatayı gider.** Şeffaf metin PNG'sini, nihai PNG'yi ve manifest'i ayrı kaydet. Görsel modelinin içine yazdığı metni ikinci katmanla kapatmaya çalışma; yazısız sahneyi yeniden üret.

### 5. Kontrol et ve yinele

`references/qa-checklist.md` ve P5 için `references/quality-gate.md` ile denetle. Karakter dekor olarak kalıyorsa, metin taşıyorsa, Türkçe karakter/etiket hatası varsa, zemin kirliyse, yapı anlaşılmıyorsa veya çizim bir sunum sayfasını andırıyorsa düzenle ya da yeniden üret. **Hatalı etiketi doğruymuş gibi sunma.**

### 6. Teslim et

Çalışma alanı varsa çıktıları `assets/<metin-kisa-adi>-illustrations/` içine sıralı kaydet: `01-konu.png`, `02-konu.png`. Önceden oluşturulmuş görselleri açık istek olmadan üzerine yazma.

Teslim özetinde görsel sayısını, her görselin kullanım yerini, nihai PNG / şeffaf metin katmanı / JSON / manifest dosyalarının **gerçek** kayıt yollarını belirt. Kaydedilmemiş dosya için yol uydurma. Herhangi bir yazılımsal kontrolü semantik doğruluk veya görsel estetik garantisi olarak sunma.

## Başarı ölçütü

Okuyucu önce küçük bir tuhaflık görmeli, hemen ardından anlatılmak istenen **tek temel ilişkiyi** kavramalı. Serbest modda görsel bir ders slaydı gibi görünmemeli; teknik modda okunaklı şema olması bilinçli bir istisnadır.
