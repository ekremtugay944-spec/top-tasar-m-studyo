# 1. Keşif Notları

## Şablon Analizleri

### Volleyball_template.svg (volleyball.ai)
- **Canvas / viewBox:** 1122.52 x 793.70667 px, viewBox="0 0 1122.52 793.70667"
- **Panel Sayısı:** 18
- **Layer Yapısı:** Tek bir `<g>` grubu içerisinde tüm `<path>` etiketleri sıralanmış (`id="path1"`'den `path18`'e kadar).
- **Renklendirme ve Stroke:** Her panelin `style` özelliği var. (Örnek: `style="fill:#006ebb;fill-opacity:1;stroke:#231916;stroke-width:1;"`) Renk değişimi doğrudan `style` içindeki `fill` güncellenerek yapılabilir.

### Soccer_filled_reference.svg (SA.ai)
- **Canvas / viewBox:** 1122.52 x 793.70667 px, viewBox="0 0 1122.52 793.70667"
- **Panel Sayısı:** 105 path bulunuyor. 32 ana panel dışında iç detaylar, dikişler ve kalınlaştırılmış hatlar olabilir.
- **Layer Yapısı:** 2 adet `<g>` (grup) var.
- **Renklendirme:** `style` özelliği kullanılarak fill ve stroke değerleri atanmış.

### Soccer_template.svg (Soccer Ball.ai)
- **Canvas / viewBox:** 1122.52 x 793.70667 px, viewBox="0 0 1122.52 793.70667"
- **Path Sayısı:** 14,104. Bu çok yüksek bir sayı; büyük ihtimalle Illustrator'deki mesh çizgileri, rehber çizgiler veya karmaşık bir maske yapısı SVG'ye path olarak aktarılmış.
- **Tavsiye:** `Soccer Ball.ai` dosyasındaki çok sayıda path, üzerinde işlem yapmayı (özellikle frontend tarafında canlı SVG editlemeyi) yavaşlatabilir. Ancak üreticinin asıl şablonu buysa `fill` değişikliğini sadece ana panel path'lerine uygulamak için belirli id/style eşleşmelerine bakmak gerekecek. `SA.ai` dosyasındaki 105 path'lik yapı çok daha temizdir. Şimdilik orijinal dosyaya sadık kalarak `soccer_blank.svg` olarak kaydediyoruz.

## Sonuç
- İki SVG dosyası da CSS `style` bazlı fill ve stroke kullanmaktadır.
- Python (`generator.py`) ve JS (`designer.html`) kodları `path` etiketlerinin `style` özelliğini parse edip değiştirerek çalışmalıdır.
- Dosyalar `templates/` klasörüne kopyalanacaktır.
