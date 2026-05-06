# Antigravity Prompt — Top Tasarım Sistemi

Aşağıdaki promptu Antigravity'de açtığın `ft-vb-sablonlar` klasörünün kök dizinine yapıştır. Bir defa çalıştır, sistemi kursun. Sonrasında her yeni top tasarımı için sadece doğal dil tarif edeceksin.

---

# GÖREV

Bu klasörde Çinli top üreticisinden alınmış 3 adet boş/dolu vektörel şablon var:
- `Soccer Ball.ai` — boş futbol topu şablonu (panel hatları çizilmiş, panel içleri renksiz)
- `volleyball.ai` — boş voleybol topu şablonu
- `SA.ai` — dolu (renklendirilmiş) bir futbol topu örneği — referans/öğrenme amaçlı

Bu şablonlar üreticinin üretim hattında kullandığı tek geçerli formattır. Üreticiye **birebir aynı yapıda** dosya gönderebilmek zorundayım.

Senden istediğim: bana doğal dilde bir top tarif ettiğimde (panel renkleri, desenleri, logolar, gradyanlar dahil), bu şablonların yapısını koruyarak üreticinin kabul edeceği formatta yeni bir vektörel dosya üreten bir sistem kurman.

---

# 1. KEŞİF AŞAMASI (sadece bir defa çalıştır)

Şu adımları sırayla yap ve bulduklarını `KESIF_NOTLARI.md` dosyasına yaz:

## 1.1 Dosyaları parse et

`.ai` dosyaları PostScript tabanlıdır, text editörle açılıp okunabilir. Önce şu komutları çalıştır:

```bash
file "Soccer Ball.ai"
file "volleyball.ai"
file "SA.ai"
head -c 2000 "Soccer Ball.ai"
```

Eğer dosyalar PDF-uyumlu .ai ise (modern Illustrator default'u), `pdftocairo` ile SVG'ye dönüştür:

```bash
pdftocairo -svg "Soccer Ball.ai" soccer_template.svg
pdftocairo -svg "volleyball.ai" volleyball_template.svg
pdftocairo -svg "SA.ai" soccer_filled_reference.svg
```

Eğer eski format .ai ise (saf PostScript), `inkscape` ile dönüştür:

```bash
inkscape "Soccer Ball.ai" --export-type=svg --export-filename=soccer_template.svg
```

Hiçbiri çalışmazsa kullanıcıya bildir, dur.

## 1.2 Şablon yapısını analiz et

Üretilen SVG dosyalarını oku ve şunları belirle:

- **viewBox / canvas boyutu** — yeni dosyanın boyutu birebir aynı olmalı
- **Panel sayısı** — futbolda kaç parça? voleybolda kaç parça?
- **Panel path tanımları** — her panelin SVG path verisi (`d="..."`)
- **Layer yapısı** — gruplar nasıl organize edilmiş? (`<g>` etiketleri)
- **Çizgi kalınlıkları, stroke renkleri** — dikiş hatları için
- **SA.ai'da kullanılan renklendirme yöntemi** — `fill` attribute mı, CSS mi, ayrı path mi?

Bunları `KESIF_NOTLARI.md`'ye yapısal olarak yaz. Örnek format:

```
## Soccer Ball.ai
- Canvas: 1000x1000 px, viewBox="0 0 1000 1000"
- Panel sayısı: 32 (20 hexagon + 12 pentagon)
- Panel path'leri: <g id="panels"> içinde, her biri ayrı <path id="panel-N">
- Stroke: #000000, width=2px (dikiş çizgileri)
- SA.ai'da renklendirme: her panel path'ine fill="#XXXXXX" eklenmiş
```

## 1.3 Şablon dosyalarını referans olarak sakla

`templates/` klasörü oluştur, içine şunları koy:
- `templates/soccer_blank.svg` — temizlenmiş boş futbol şablonu
- `templates/volleyball_blank.svg` — temizlenmiş boş voleybol şablonu
- `templates/soccer_filled_example.svg` — SA.ai'nın SVG hali (öğrenme/karşılaştırma için)

---

# 2. SİSTEM MİMARİSİ

Klasör yapısı şu olacak:

```
ft-vb-sablonlar/
├── Soccer Ball.ai          (orijinal — DOKUNMA)
├── volleyball.ai            (orijinal — DOKUNMA)
├── SA.ai                    (orijinal — DOKUNMA)
├── KESIF_NOTLARI.md         (1. aşamadan)
├── templates/
│   ├── soccer_blank.svg
│   ├── volleyball_blank.svg
│   └── soccer_filled_example.svg
├── designer.html            (kullanıcı arayüzü)
├── generator.py             (SVG üretim motoru)
├── output/                  (üretilen dosyalar buraya)
└── README.md                (kullanım kılavuzu)
```

## 2.1 `designer.html` — Kullanıcı Arayüzü

Tek HTML dosyası, modern ve temiz tasarım. Şu özellikler:

**Üst kısım — Top tipi seçimi:**
- Radio: ⚽ Futbol Topu / 🏐 Voleybol Topu

**Sol panel — Hızlı Seçim Aracı:**
- Panel renkleri: renk paleti (her panel için ayrı renk seçimi mümkün)
- Hazır şablonlar: "Klasik siyah-beyaz", "Tek renk", "Şerit", "Bayrak (3 renk)", "Geometrik", "Custom"
- Logo yükleme: drag & drop alanı (PNG/SVG)
- Logo yerleşimi: panel seçimi (hangi panele logo gelsin?)
- Desen tipi: Düz / Çizgi / Yıldız / Nokta / Gradyan
- Gradyan opsiyonu: 2 renk seçici + yön

**Alt kısım — Doğal Dil Girişi:**
Büyük textarea: "Topu doğal dilde de anlat — örnek: 'kırmızı-beyaz alternatif paneller, ortadaki panele altın yıldız, dikiş çizgileri siyah'"

**Sağ panel — Önizleme:**
- Canlı SVG önizleme (girdi değiştikçe güncellenir)
- "Üret ve indir" butonu → `output/` klasörüne kayıt + tarayıcıdan indirme

**Önizleme nasıl çalışır:**
- Form değiştiğinde JavaScript, `templates/soccer_blank.svg`'yi yükler, panellerin `fill` değerlerini güncelleyip ekranda gösterir
- Gradyan ve desen için inline `<defs>` ekler

**Doğal dil girişi nasıl işlenir:**
- "Üret" tıklandığında, doğal dil metni varsa Anthropic API'ye gönderilir
- API'den dönen yapılandırılmış JSON form alanlarını otomatik doldurur
- Sonra normal üretim akışı çalışır

API çağrısı şöyle olacak (Antigravity'nin API key'i hazır):

```javascript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "claude-sonnet-4-5",
    max_tokens: 1024,
    messages: [{
      role: "user",
      content: `Aşağıdaki top tasarımı tarifini yapılandırılmış JSON'a çevir.
      
Tarif: "${userText}"

Sadece şu formatta JSON döndür, başka hiçbir şey yazma:
{
  "ball_type": "soccer" veya "volleyball",
  "panels": [{"index": 0, "fill": "#HEXKOD"}, ...],
  "stroke_color": "#HEXKOD",
  "logo": null veya {"panel_index": N, "data_url": "..."},
  "pattern": null veya {"type": "stripes/stars/dots/gradient", "colors": [...], "direction": "..."}
}`
    }]
  })
});
```

## 2.2 `generator.py` — SVG Üretim Motoru

Python script, hem CLI hem `designer.html`'den çağrılabilir.

**Girdi:** JSON dosyası veya stdin'den JSON
```json
{
  "ball_type": "soccer",
  "panels": [{"index": 0, "fill": "#FF0000"}, {"index": 1, "fill": "#FFFFFF"}, ...],
  "stroke_color": "#000000",
  "logo": {"panel_index": 5, "svg_path": "logo.svg"},
  "pattern": null
}
```

**İşleyiş:**
1. `templates/{ball_type}_blank.svg` dosyasını oku
2. SVG'yi parse et (lxml veya xml.etree)
3. Her panel için `fill` attribute'unu güncelle
4. Stroke renklerini güncelle
5. Logo varsa: hedef panelin bbox'ını hesapla, logo SVG'sini o bbox'a `<g transform>` ile yerleştir
6. Pattern varsa: `<defs>` içine `<pattern>` veya `<linearGradient>` ekle, ilgili panelin fill'ini `url(#patternId)` yap
7. Sonucu `output/` klasörüne `topu_YYYYMMDD_HHMMSS.svg` olarak kaydet
8. Aynı dosyayı `topu_YYYYMMDD_HHMMSS.pdf` olarak da kaydet (cairosvg ile) — Illustrator bunu da `.ai` olarak açabilir

**ÖNEMLİ:** Üretilen SVG'nin path verileri, viewBox'u, layer yapısı orijinal şablonla **birebir aynı** olmalı. Sadece renk/fill/desen değişebilir. Bu üreticinin formatı bozmaması için kritik.

## 2.3 `README.md`

Türkçe, kısa kullanım kılavuzu:
- Sistemi nasıl başlatırım? (`python -m http.server 8000` → `designer.html`'i aç)
- Çıktı .ai'ye nasıl dönüştürülür? (Illustrator'da SVG'yi aç → "Save As .ai")
- Yeni şablon eklemek istersem ne yapmalıyım?

---

# 3. KALİTE KONTROLLERİ

Sistemi kurduktan sonra şunu test et:
1. `templates/soccer_blank.svg`'yi al, tüm panelleri `#FF0000` yap, çıktıyı üret
2. Çıktıyı `templates/soccer_filled_example.svg` ile karşılaştır — yapı (path'ler, viewBox, layer'lar) aynı mı?
3. Aynısını voleybol için yap

Eğer yapı korunmuyorsa, `generator.py`'da SVG manipülasyonunu düzelt. **Path verilerine asla dokunma**, sadece attribute'ları güncelle.

---

# 4. KISITLAR VE NOTLAR

- Kullanıcının dili Türkçe — tüm UI metinleri ve hata mesajları Türkçe olsun
- Üretilen dosya adı Türkçe karakter içermesin (üretici sistemiyle uyum için): `top_2026_05_06_142533.svg` formatı
- Original `.ai` dosyalarını **asla** değiştirme — read-only kabul et
- Kod yazarken token verimli ol: aynı işi iki yerde yapma, gereksiz kütüphane ekleme
- Bağımlılıklar minimum: Python tarafında `lxml` + `cairosvg`, frontend'de saf JS (framework yok)

---

# 5. BAŞLANGIÇ

İlk yapacakların sırası:
1. Klasördeki dosyaları kontrol et (`ls`)
2. **1.1 ve 1.2** keşif adımlarını çalıştır, `KESIF_NOTLARI.md` üret
3. Bulduklarını bana özetle, devam etmeden önce onayımı bekle
4. Onay sonrası `templates/`, `generator.py`, `designer.html`, `README.md` dosyalarını sırayla oluştur
5. Bölüm 3'teki kalite testini çalıştır, sonucunu raporla

Her adımda ne yaptığını kısaca açıkla. Bilmediğin bir şey çıkarsa tahmin etme, sor.
