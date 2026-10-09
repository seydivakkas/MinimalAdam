# Görsel Üretim İstemleri — Türkçe

Her çizimi **ayrı** üret. Köşeli parantez içindeki alanları kullanıcı metnine göre doldur; birden fazla görseli tek kolajda birleştirme.

## Tek bir yazısız temel sahne üret (P2 varsayılanı)

```text
Türkçe bir makale için bağımsız, yatay 16:9 oranında tek bir açıklayıcı illüstrasyon üret.

Görsel kimlik:
Bembeyaz ve tamamen düz arka plan. İnce, hafif düzensiz siyah el çizimi çizgiler. Bol boşluk. Gerekli yerlerde çok az kırmızı, turuncu ve mavi vurgu. Soyut bir ürün fikrini elle çizilmiş sıra dışı fiziksel mecazla anlat. Gölgeler, gradyanlar, kâğıt dokusu, karmaşık arka planlar, ticari vektör estetiği, PPT görünümü, sevimli maskot afişi, çocuk kitabı çizimi ve gerçekçi arayüz görünümü olmasın.

Ana karakter:
MinimalAdam: siyah, küçük ve dolu gövdeli; iki beyaz nokta gözlü, ince bacaklı, hafif düzensiz siluetli, ciddi ve ifadesiz bir karakter. Ana fikri anlatan işi MinimalAdam yapmalı; kenarda sadece seyretmemeli. Çocuksu veya aşırı sevimli olmasın.

Konu:
[KONU]

Kompozisyon türü:
[İş akışı / Sistemin bir kesiti / Öncesi ve sonrası / Karakter durumları / Kavramsal mecaz / Yöntem katmanları / Harita ve rota / Kısa çizgi roman]

Tek ana fikir:
[ANA FİKİR]

Sahne:
[MINIMALADAM NEREDE, NE YAPIYOR, NESNELER VE BİLGİ AKIŞI NASIL YERLEŞİYOR?]

Önemli öğeler:
[ÖĞE 1] / [ÖĞE 2] / [ÖĞE 3] / [İSTEĞE BAĞLI ÖĞE 4]

Sonradan ayrı katmanda eklenecek Türkçe kısa etiketler (sahneye YAZMA):
[ETİKET 1] / [ETİKET 2] / [ETİKET 3] / [ETİKET 4] / [İSTEĞE BAĞLI ETİKET 5]

**ZORUNLU:** Bu aşamada sahnenin hiçbir yerinde harf, sayı, başlık, sahte el yazısı, logo, tabela, kod veya okunabilir işaret üretme. Görseli yalnız çizgi ve şekillerle oluştur. Yazıları sonradan JSON üzerinden ayrı katmana gerçek sistem fontuyla ekle.

Renkler:
Siyah ana çizim ve MinimalAdam için. Turuncu ana akış ve oklar için. Kırmızı yalnızca kritik uyarı, sorun ya da sonuç için. Mavi yalnızca ikincil açıklama ve sistem geri bildirimi için.

Sınırlar:
Bir çizim bir ana fikri anlatsın. Ana sahne tuvalin yaklaşık %40–60'ını kaplasın, en az %35'i beyaz boşluk kalsın. Etiket sayısı en çok 5–8 ve mümkünse daha az olsun. Sol üste tür başlığı yazma. Görsele 'Akış Şeması' veya 'Sistem Mimarisi' gibi bir başlık ekleme. Düzenli kutu ve oklardan oluşan resmi diyagram ya da ders slaydı yapma. Önceden görülen örnek sahneleri kopyalama; bu içeriğe özgü yeni, biraz tuhaf ama anlaşılır bir mecaz üret.
```

## Var olan görselden başlığı kaldır

```text
Bu görseli düzenle. Sol üst köşedeki '[SİLİNECEK METİN]' ifadesini ve ona ait alt çizgiyi kaldır. Bölgeyi çevresiyle aynı saf beyaz arka planla doldur. Karakterleri, diğer doğru etiketleri, çizgileri, yerleşimi, en-boy oranını ve kaliteyi koru. Yeni yazı veya nesne ekleme.
```

## MinimalAdam'ın ana eylemini güçlendir

```text
Görselin temel fikrini ve sade düzenini koruyarak yeniden üret. MinimalAdam, anlamı yaratan kritik işi bizzat gerçekleştirsin; şemanın yanında dekor gibi durmasın. Yeni mecaz daha özgün ve biraz daha sıra dışı olsun. Beyaz zemin, bol boşluk, hafif el çizimi ve kısa Türkçe etiketler korunmalı. Sevimli maskot görünümünden kaçın.
```

## Hatalı Türkçe etiketi düzelt

```text
Bu görselde yalnızca '[YANLIŞ ETİKET]' yazısını doğru Türkçe biçimi '[DOĞRU ETİKET]' ile değiştir. Türkçe karakterleri tam olarak koru. Konumu, el yazısı çizgi hissini, diğer metinleri ve tüm çizimi değiştirme. Düzenleme doğru yazıyı sağlayamıyorsa etiketi kaldırıp doğru Türkçe yazıyı ayrı katmanda eklemek için düzenlenebilir bir iş akışı öner.
```

## Sonradan Türkçe etiket ekleme (P2)

Çizim üzerine doğrudan yazı üreten istem yerine `references/turkish-text-layer.md` kurallarını izle. Girdi: yazısız `*.base.png` ve UTF-8 `*.labels.json`. Çıktı: `*.png`, `*.text.png`, `*.labels.svg`, `*.manifest.json`. Türkçe sözcükleri aynen koru; otomatik çeviri veya düzeltme uygulama.
