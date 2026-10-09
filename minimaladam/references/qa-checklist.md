# Kalite Kontrol Listesi (QA)

## Zorunlu kontroller

- [ ] Yatay 16:9 oranı kullanılmış.
- [ ] Arka plan temiz ve tamamen beyaz.
- [ ] MinimalAdam mevcut.
- [ ] MinimalAdam ana kavramsal eylemi gerçekleştiriyor.
- [ ] Önceki örneğin kompozisyonu kopyalanmamış; özgün mecaz var.
- [ ] Çizim sade, akılda kalıcı ve hafif sıra dışı.
- [ ] Ana sahne yaklaşık %60'tan büyük değil; yeterli negatif alan var.
- [ ] Tek resim yalnızca bir ana yapıyı/ilişkiyi açıklıyor.
- [ ] Etiketler az, kısa ve okunabilir.
- [ ] Kullanıcı başka dil istemedikçe okunabilir etiketlerin **tamamı Türkçe**.
- [ ] `ç ğ ı İ ö ş ü` karakterleri doğru.
- [ ] Üretim temel sahnesinde yazı yok; tüm metinler ayrı katmanda.
- [ ] JSON etiketleri UTF-8/NFC, font glifleri mevcut, etiketler kendi aralarında çakışmıyor ve taşmıyor.
- [ ] `*.manifest.json` doğrulama bilgileri mevcut; çizim ile etiketin anlamsal yerleşimi insan tarafından gözden geçirildi.
- [ ] Turuncu ana yol/ok; kırmızı vurgu/sorun/sonuç; mavi ikincil açıklama/durum için kullanılmış.

## Başarısızlık işaretleri

Şunlardan biri varsa görseli düzenle veya yeniden üret:

- Sol üstte `Sık Hatalar`, `Workflow`, `Sistem Mimarisi`, `Yol Haritası` gibi gereksiz tür başlığı.
- MinimalAdam bir çıkartma veya aşırı sevimli maskot gibi duruyor.
- Görsel PPT slaydı, eğitim föyü veya resmi akış şemasına benziyor.
- Fazla nesne, ok, düğüm veya uzun açıklamalar var.
- Kâğıt dokusu, gölge, gradyan, bej veya görsel gürültü var.
- Gerçekçi arayüz ekranı veya bilim kurgu paneli var.
- Yanlış Türkçe sözcük, eksik Türkçe karakter, okunmayan etiket veya beklenmedik yabancı dil bulunuyor.
- Görselde hatırlanabilir bir eylem ya da mecaz yok.
- Özgün örneğin kompozisyonu neredeyse aynen tekrarlanmış.

## Düzeltme yöntemi

- Çok sıradansa: MinimalAdam'ı ana eylemi gerçekleştiren aktöre dönüştür ve somut mecaz ekle.
- Çok karmaşıksa: düğüm sayısını azalt; bir eylem ve 3–5 kısa etiket bırak.
- Fazla sevimliyse: ifadesiz, ciddi, sade, maskot olmayan karakter belirt.
- PPT'ye benziyorsa: başlığı, çerçeveyi, cetvelle çizilmiş ızgarayı ve fazla okları kaldır.
- Örneğe benziyorsa: ana fikri koruyup başlıca nesne ve eylemi değiştir.
- Türkçe yazı bozuksa: etiketi JSON içinde düzelt ve metin katmanını yeniden üret; temel görselde yazı varsa yazısız yeniden üret.

## Teslim koşulu

İyi çizim önce dikkat çekici ölçüde tuhaf görünür, sonra tek bakışta ana ilişkiyi anlaşılır kılar. Eğitim slaydı gibi görünmesi kalite başarısızlığıdır.

**Sınır:** Bu liste görsel kaliteyi denetler; bir metnin teknik veya bilimsel doğruluğunu kanıtlamaz.

## P3 teknik çizim istisnası

Yalnız `technical-mode.md` seçildiğinde kutu/ok, kısa gerçek düğüm adları ve ayrık katmanlar beklenen özelliklerdir. Kontrol sırası: doğru kaynak-hedef ilişkisi, geri besleme yönü, etiket tipografisi, düğüm çakışmaları, okların üçüncü düğümleri kesmemesi ve anlamın kullanıcı kaynağıyla eşleşmesi. Genel modun "PPT/şema yasak" maddesi teknik modda otomatik başarısızlık sebebi değildir.

## P5 otomatik kalite kapısı

Kural ve ölçüm ayrıntıları: [quality-gate.md](quality-gate.md). `PASS` kaynak tanımının veya çizimin semantik/estetik doğruluğunu **garanti etmez**. `NOT_VERIFIED` maddeleri bilinçli olarak insan incelemesine bırakılır. PNG üretiminde `scripts/inspect_render.py` ile beyaz alan ve renk paleti gibi yalnız piksel tabanlı kontroller uygulanabilir.
