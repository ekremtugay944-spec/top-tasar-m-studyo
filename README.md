# Top Tasarım Stüdyosu Pro

Bu sistem, üretici fabrikadan gelen boş vektörel (`.ai` / `.svg`) top şablonlarını bozmadan, doğal dil komutlarıyla veya gelişmiş arayüz üzerinden renk, desen, gradyan ve logolar giydirerek yeni üretime hazır şablonlar oluşturmanızı sağlar.

## Yeni Pro Özellikler
1. **Desen (Pattern) ve Gradyan Desteği:** Panelleri çizgili, noktalı, dalgalı desenlerle veya lineer/radyal gradyanlarla doldurabilirsiniz.
2. **Çoklu Logo Desteği:** Herhangi bir panele, opaklık ve ölçek ayarı yapılarak logo (SVG/PNG) yerleştirilebilir.
3. **Gelişmiş Claude AI Entegrasyonu:** "Barcelona temalı", "çocuk topu", "lüks tasarım" gibi soyut konseptler saniyeler içinde yapılandırılmış tasarıma dönüştürülür.
4. **Tasarım Kütüphanesi:** Yaptığınız tasarımları tarayıcıya (localStorage) kaydedip daha sonra yükleyebilir veya çoğaltabilirsiniz.
5. **Hızlı Başlangıç Şablonları:** Klasik, Türkiye, Galatasaray, Fenerbahçe, Lüks Altın gibi hazır şablonlar ile tasarıma 1 tıkla başlayabilirsiniz.

## Kurulum ve Çalıştırma

1. **Gereksinimler:**
   - Python 3.x
   - (Opsiyonel) Çıktı olarak PDF de almak isterseniz: `pip install cairosvg`

2. **Sistemi Başlatma:**
   Klasör dizininde terminali açın ve şu komutu çalıştırın:
   ```bash
   python -m http.server 8000
   ```
   Ardından tarayıcınızdan http://localhost:8000/designer.html adresine gidin.

## Kullanım

### Arayüz Üzerinden (designer.html)
- Sol taraftan **Model Seçimi** yapın veya **Hızlı Şablonlar** butonuna tıklayarak bir tema yükleyin.
- Orta alandaki **Paneller** bölümünden dilediğiniz panelin dolgu tipini (düz, gradyan, desen) değiştirebilirsiniz.
- **Logolar** kısmından URL veya base64 girerek istediğiniz panel indeksine logo yerleştirebilirsiniz.
- Sağ alt köşede bulunan **"AI Studio"** kısmında Anthropic API anahtarınızı (sağ üst) girerek tasarımı doğal dilde tarif edin.
- İşiniz bitince **Üretim JSON İndir** butonuna tıklayarak tasarımı kaydedin.

### Terminal Üzerinden Üretim (generator.py)
Arayüzden indirdiğiniz veya kendiniz oluşturduğunuz JSON dosyasını `generator.py`'ye vererek SVG üretebilirsiniz:
```bash
python generator.py indirilen_tasarim.json
```
Üretilen SVG dosyaları otomatik olarak `output/` klasörüne kaydedilir.

## Üretici İçin .AI Formatına Dönüştürme
Üretilen sistem SVG çıktıları verir. Orijinal dosyadaki tüm teknik çizim katmanları, viewBox ve panel yapıları (topology) korunur.
1. `output/` içindeki SVG dosyasını **Adobe Illustrator** programında açın.
2. `File > Save As` (Dosya > Farklı Kaydet) seçeneğine tıklayın.
3. Format olarak **Adobe Illustrator (*.AI)** seçin ve kaydedin.
4. Bu dosya üreticinin kabul edeceği geçerli yapıdadır.
