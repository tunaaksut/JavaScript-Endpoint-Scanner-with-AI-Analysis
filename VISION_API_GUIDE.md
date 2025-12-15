# 🎯 Vision API + Structured Outputs - Kullanım Rehberi

## 🆕 Yeni Özellikler

Bu güncellemede iki kritik OpenAI özelliği eklendi:

### 1. **Vision API (Görsel Analiz)**
- Her sayfanın ekran görüntüsünü (screenshot) alır
- OpenAI'ın gpt-4o-mini veya gpt-4o modeli ile analiz eder
- Kodda görünmeyen güvenlik açıklarını tespit eder:
  - ❌ Stack traces (hata mesajları)
  - 🐛 Debug mode uyarıları
  - 🔑 API key sızıntıları
  - 🔓 Admin panel giriş formları
  - 💾 Veritabanı hataları

### 2. **Structured Outputs (JSON Garantisi)**
- OpenAI API'den gelen yanıtlar **kesinlikle geçerli JSON**
- Regex veya string parsing KULLANILMIYOR
- `response_format={"type": "json_object"}` ile garanti
- Doğrudan `json.loads()` çalışır

---

## 📸 Screenshot (Vision API) Kullanımı

### Temel Kullanım

```powershell
# Screenshot'ları yakala ve Vision API ile analiz et
python scan_website.py https://example.com --screenshots

# Sadece 5 sayfa tara + screenshot
python scan_website.py https://example.com --pages 5 --screenshots

# gpt-4o modeli ile (daha detaylı analiz)
python scan_website.py https://example.com --screenshots --ai-model gpt-4o
```

### Sadece Vision Analizi

```powershell
# Önce normal tarama (screenshot ile)
python scan_website.py https://example.com --screenshots --no-ai

# Sonra sadece Vision analizi çalıştır
python analyze_with_ai.py scan-example.com.json --vision-only
```

---

## 🔧 Yeni Parametreler

### scan_website.py

```powershell
python scan_website.py <URL> [OPTIONS]

OPTIONS:
  --screenshots         # Screenshot'ları yakala (Vision API için)
  --pages N             # Maksimum sayfa sayısı (default: 10)
  --depth N             # Maksimum tarama derinliği (default: 2)
  --ai-model MODEL      # AI model (gpt-3.5-turbo, gpt-4o, gpt-4o-mini)
  --vision-only         # Sadece Vision analizi (endpoint analizi yok)
  --no-ai               # AI analizi çalıştırma (sadece tarama)
```

### analyze_with_ai.py

```powershell
python analyze_with_ai.py <SCAN_FILE> [OPTIONS]

OPTIONS:
  --model MODEL         # Endpoint için: gpt-3.5-turbo, gpt-4
                        # Vision için: gpt-4o-mini, gpt-4o
  --vision-only         # Sadece Vision analizi çalıştır
```

---

## 📊 Çıktı Formatları

### Endpoint Analizi (Structured Output)

```json
{
  "endpoint_analysis": {
    "analysis": [
      {
        "endpoint": "DELETE /api/users/{userId}",
        "risk_detected": true,
        "risk_level": "Critical",
        "risk_type": "IDOR",
        "reasoning": "userId parametresi ile başka kullanıcılar silinebilir",
        "cvss_score": 9.1
      }
    ]
  }
}
```

### Vision Analizi (Structured Output)

```json
{
  "visual_analysis": [
    {
      "url": "https://example.com/dashboard",
      "issues_found": true,
      "description": "Sayfanın sağ alt köşesinde 'Development Mode Enabled' yazısı ve bir stack trace hatası görünüyor.",
      "severity": "Medium"
    }
  ]
}
```

---

## 💰 Maliyet Bilgisi

### Endpoint Analizi
- **gpt-3.5-turbo**: ~$0.0005 per scan (ÖNERİLEN)
- **gpt-4**: ~$0.02 per scan (daha detaylı)

### Vision Analizi
- **gpt-4o-mini**: ~$0.001 per screenshot (ÖNERİLEN)
- **gpt-4o**: ~$0.005 per screenshot (çok detaylı)

**Örnek Maliyet:**
- 10 sayfa tarama + 10 screenshot
- Endpoint analizi: gpt-3.5-turbo ($0.0005)
- Vision analizi: gpt-4o-mini x10 ($0.01)
- **TOPLAM: ~$0.01** (1 sent)

---

## 🎯 Pratik Örnekler

### Örnek 1: Hızlı Tarama (Ucuz)
```powershell
# 5 sayfa, screenshot YOK, gpt-3.5-turbo
python scan_website.py https://example.com --pages 5

# Maliyet: ~$0.0005
```

### Örnek 2: Tam Analiz (Screenshot + Vision)
```powershell
# 15 sayfa, screenshot VAR, gpt-4o-mini
python scan_website.py https://example.com --pages 15 --screenshots --ai-model gpt-4o-mini

# Maliyet: ~$0.015 (endpoint + 15 screenshot)
```

### Örnek 3: Premium Analiz (En Detaylı)
```powershell
# 20 sayfa, screenshot VAR, gpt-4o
python scan_website.py https://example.com --pages 20 --screenshots --ai-model gpt-4o

# Maliyet: ~$0.12 (gpt-4 endpoint + gpt-4o vision x20)
```

### Örnek 4: Sadece Vision (Önceden Taranmış Site)
```powershell
# Önce screenshot'lı tarama
python scan_website.py https://example.com --screenshots --no-ai

# Sonra sadece Vision analizi
python analyze_with_ai.py scan-example.com.json --vision-only

# Maliyet: Sadece Vision (~$0.01 for 10 screenshots)
```

---

## 🔍 Neleri Tespit Eder?

### Endpoint Analizi (Kod Bazlı)
✅ **IDOR** - Insecure Direct Object Reference  
✅ **BOLA** - Broken Object Level Authorization  
✅ **SSRF** - Server-Side Request Forgery  
✅ **Mass Assignment** - Aşırı parametre kabul eden endpoint'ler  
✅ **Information Disclosure** - Hassas bilgi sızdıran endpoint'ler  
✅ **Admin Access** - /admin, /internal gibi hassas path'ler

### Vision Analizi (Görsel Bazlı)
✅ **Stack Traces** - Kod hata mesajları  
✅ **Debug Mode** - Development/Test mode uyarıları  
✅ **SQL Errors** - Veritabanı hatası mesajları  
✅ **API Keys** - Ekranda görünen gizli anahtarlar  
✅ **Admin Panels** - Giriş formları, dashboard'lar  
✅ **Console Logs** - Şüpheli browser console çıktıları

---

## 🚨 Uyarılar

### Screenshot Boyutu
- Her screenshot ~100KB (base64 encoded)
- 50 sayfa = ~5MB JSON dosyası
- Makul limit: **10-20 screenshot per scan**

### Token Limitleri
- Vision API: Her screenshot için ~1000-2000 token
- 10 screenshot = ~15,000 token
- Rate limit: GPT-4o-mini için 200 request/min

### Öneriler
- ✅ İlk taramada 5-10 sayfa kullan
- ✅ gpt-4o-mini kullan (maliyet-etkin)
- ✅ Sadece hassas sayfalar için screenshot al
- ❌ 50+ sayfa için screenshot alma (çok maliyetli)

---

## 📝 Sonuç Dosyaları

### Tarama Sonucu
```
scan-example.com.json
```
- Endpoint listesi
- Network log
- Screenshot'lar (base64)
- İstatistikler

### AI Analiz Sonucu
```
scan-example.com-ai-analysis.json
```
- Endpoint güvenlik analizi
- Vision görsel analizi
- Risk seviyeleri + CVSS skorları

---

## 🎓 Best Practices

### 1. İlk Tarama (Keşif)
```powershell
# Screenshot olmadan hızlı tarama
python scan_website.py https://target.com --pages 20 --no-ai

# Manuel olarak sonuçları incele
```

### 2. Hedefli Analiz (Şüpheli Endpoint'ler)
```powershell
# Şimdi AI analizi çalıştır
python analyze_with_ai.py scan-target.com.json
```

### 3. Vision Analizi (Hassas Sayfalar)
```powershell
# Sadece kritik sayfalar için screenshot
python scan_website.py https://target.com/admin --pages 5 --screenshots --depth 1
```

---

## 🛠️ Troubleshooting

### JSON Parse Hatası
```
❌ JSON parse hatası: Expecting property name
```
**Çözüm:** Structured Outputs kullanıyoruz, bu hata ASLA çıkmamalı.  
Eğer çıkarsa: OpenAI API'de `response_format` parametresi eksik.

### Screenshot Alınamadı
```
⚠️  Screenshot capture failed for https://example.com
```
**Çözüm:** 
- Sayfa yüklenmesi çok yavaş olabilir (timeout)
- JavaScript hatası olabilir (sayfada)
- Playwright headless modda çalışmayabilir

### Vision API Çok Pahalı
```
💸 10 screenshot = $0.05 (gpt-4o)
```
**Çözüm:**
- `gpt-4o-mini` kullan (5x daha ucuz)
- Screenshot sayısını azalt (--pages 5)
- `detail: "low"` kullan (otomatik yapılıyor)

---

## 📞 Destek

Sorularınız için:
- GitHub Issues: https://github.com/tunaaksut/JavaScript-Endpoint-Scanner-with-AI-Analysis/issues
- Email: tunaaksut44@gmail.com

---

**Son Güncelleme:** Vision API + Structured Outputs entegrasyonu
**Versiyon:** 2.0 (Aralık 2025)
