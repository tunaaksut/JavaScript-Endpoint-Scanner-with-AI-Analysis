"""
AI-Powered Endpoint Security Analyzer with Vision API
OpenAI ile endpoint güvenlik analizi + Görsel hata tespiti

Kullanım:
    python analyze_with_ai.py scan-www.lcw.com.json
    python analyze_with_ai.py scan-www.lcw.com.json --model gpt-4o
    python analyze_with_ai.py scan-www.lcw.com.json --vision-only  # Sadece görsel analiz
"""

import json
import sys
import os
from openai import OpenAI
from typing import List, Dict

def load_scan_results(json_file):
    """Scan sonuçlarını yükle"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_endpoints_with_ai(endpoints: List[Dict], api_key: str, model: str = "gpt-3.5-turbo") -> Dict:
    """
    OpenAI Structured Outputs ile endpoint güvenlik analizi
    
    STRUCTURED OUTPUT GUARANTEE:
    - response_format ile JSON garantisi
    - Regex/string parsing YOK
    - Doğrudan json.loads() çalışır
    
    Returns:
        {
            "analysis": [
                {
                    "risk_detected": bool,
                    "risk_level": str,  # Critical/High/Medium/Low/Info
                    "risk_type": str,   # IDOR/BOLA/SSRF/etc
                    "reasoning": str,
                    "endpoint": str
                }
            ]
        }
    """
    
    client = OpenAI(api_key=api_key)
    
    # Endpoint listesini hazırla (ilk 50)
    endpoint_summary = []
    for ep in endpoints[:50]:
        endpoint_summary.append({
            'method': ep['method'],
            'url': ep['url_template'],
            'parameters': [p['name'] for p in ep.get('parameters', [])]
        })
    
    # Structured Output için JSON Schema
    response_schema = {
        "type": "object",
        "properties": {
            "analysis": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "endpoint": {"type": "string"},
                        "risk_detected": {"type": "boolean"},
                        "risk_level": {
                            "type": "string",
                            "enum": ["Critical", "High", "Medium", "Low", "Info"]
                        },
                        "risk_type": {
                            "type": "string",
                            "enum": ["IDOR", "BOLA", "SSRF", "Mass Assignment", "Information Disclosure", "Admin Access", "None"]
                        },
                        "reasoning": {"type": "string"},
                        "cvss_score": {"type": "number"}
                    },
                    "required": ["endpoint", "risk_detected", "risk_level", "risk_type", "reasoning"]
                }
            }
        },
        "required": ["analysis"]
    }
    
    # AI prompt
    prompt = f"""Sen bir API güvenlik uzmanısın. Aşağıdaki endpoint'leri analiz et:

{json.dumps(endpoint_summary, indent=2)}

Her endpoint için tespit et:
1. IDOR - userId/orderId parametreleri
2. BOLA - Yetkilendirme zafiyeti
3. SSRF - URL parametresi
4. Mass Assignment - Çok parametre
5. Information Disclosure - Hassas veri
6. Admin Access - /admin path'leri

risk_detected=true ise mutlaka reasoning açıkla."""
    
    print("🤖 Endpoint Analizi (Structured Output)...")
    print(f"📊 {len(endpoint_summary)} endpoint")
    print(f"🔧 Model: {model}\n")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Sen bir API güvenlik uzmanısın. JSON formatında structured output üret."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},  # STRUCTURED OUTPUT GUARANTEE
            temperature=0.3,
            max_tokens=3000
        )
        
        # DOĞRUDAN JSON.LOADS (regex/parsing YOK!)
        ai_response = response.choices[0].message.content
        analysis = json.loads(ai_response)
        
        print(f"✅ Analiz tamamlandı: {len(analysis.get('analysis', []))} endpoint değerlendirildi\n")
        return analysis
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse hatası: {e}")
        return {"error": "JSON decode failed", "analysis": []}
    except Exception as e:
        print(f"❌ AI analizi hatası: {e}")
        return {"error": str(e), "analysis": []}

def analyze_screenshots_with_vision(screenshots: List[Dict], api_key: str, model: str = "gpt-4o-mini") -> Dict:
    """
    OpenAI Vision API ile ekran görüntülerini analiz et
    
    GÖRSEL HATA TESPİTİ:
    - Stack traces (kod hataları)
    - Debug mode mesajları
    - Admin panelleri
    - Hassas bilgi sızıntısı
    
    STRUCTURED OUTPUT ile JSON garantisi
    
    Args:
        screenshots: [{"url": str, "base64_image": str, ...}]
        api_key: OpenAI API key
        model: gpt-4o veya gpt-4o-mini (vision destekli)
    
    Returns:
        {
            "visual_analysis": [
                {
                    "url": str,
                    "issues_found": bool,
                    "description": str,
                    "severity": str  # Critical/High/Medium/Low/Info
                }
            ]
        }
    """
    
    if not screenshots:
        print("ℹ️  Screenshot bulunamadı - Vision analizi atlanıyor")
        return {"visual_analysis": []}
    
    client = OpenAI(api_key=api_key)
    
    print(f"👁️  Vision Analizi Başlatılıyor...")
    print(f"📸 {len(screenshots)} screenshot analiz edilecek")
    print(f"🔧 Model: {model}\n")
    
    all_results = []
    
    for idx, screenshot in enumerate(screenshots[:10], 1):  # İlk 10 screenshot (maliyet kontrolü)
        url = screenshot.get('url', 'unknown')
        base64_image = screenshot.get('base64_image', '')
        
        if not base64_image:
            continue
        
        print(f"  [{idx}/{min(len(screenshots), 10)}] Analiz ediliyor: {url[:60]}...")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "Sen bir güvenlik uzmanısın. Web sayfası görüntülerinde güvenlik açıklarını tespit ediyorsun."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Bu web sayfası görüntüsünde GÜVENLİK SORUNLARI var mı?

Ara:
- Stack traces (hata mesajları)
- "Development Mode", "Debug Mode" yazıları
- Veritabanı hataları (SQL errors)
- API key'ler veya token'lar
- Admin/Dashboard giriş formları
- Şüpheli console logları

issues_found=true ise mutlaka description yaz.

JSON formatında yanıtla:
{
  "issues_found": boolean,
  "description": "string",
  "severity": "Critical|High|Medium|Low|Info"
}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "low"  # "low" daha ucuz, "high" daha detaylı
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},  # STRUCTURED OUTPUT
                temperature=0.2,
                max_tokens=500
            )
            
            # JSON parse (doğrudan çalışır)
            ai_response = response.choices[0].message.content
            result = json.loads(ai_response)
            
            # URL ekle
            result['url'] = url
            all_results.append(result)
            
            # Sonucu göster
            if result.get('issues_found'):
                severity = result.get('severity', 'Unknown')
                print(f"    ⚠️  {severity}: {result.get('description', 'N/A')[:80]}")
            else:
                print(f"    ✅ Sorun bulunamadı")
        
        except json.JSONDecodeError as e:
            print(f"    ❌ JSON parse hatası: {e}")
            all_results.append({
                "url": url,
                "issues_found": False,
                "description": "Parse error",
                "severity": "Info"
            })
        except Exception as e:
            print(f"    ❌ Vision analizi hatası: {e}")
            all_results.append({
                "url": url,
                "issues_found": False,
                "description": f"Error: {str(e)}",
                "severity": "Info"
            })
    
    print(f"\n✅ Vision analizi tamamlandı\n")
    return {"visual_analysis": all_results}


def display_endpoint_analysis(analysis: Dict):
    """Endpoint analiz sonuçlarını göster"""
    if 'error' in analysis:
        print(f"❌ Hata: {analysis['error']}")
        return
    
    results = analysis.get('analysis', [])
    
    if not results:
        print("ℹ️  Endpoint analizi sonucu yok")
        return
    
    # Sadece risk tespit edilenleri filtrele
    risks = [r for r in results if r.get('risk_detected')]
    
    if not risks:
        print("✅ Endpoint'lerde kritik risk tespit edilmedi!")
        return
    
    print("\n" + "=" * 60)
    print("🎯 ENDPOINT GÜVENLİK ANALİZİ")
    print("=" * 60)
    
    # Risk seviyesine göre sırala
    risk_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4}
    risks.sort(key=lambda x: risk_order.get(x.get('risk_level', 'Low'), 3))
    
    for idx, risk in enumerate(risks, 1):
        level = risk.get('risk_level', 'Unknown')
        risk_type = risk.get('risk_type', 'Unknown')
        endpoint = risk.get('endpoint', 'N/A')
        reasoning = risk.get('reasoning', 'No reasoning')
        cvss = risk.get('cvss_score', 'N/A')
        
        # Icon
        icons = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🔵', 'Info': '⚪'}
        icon = icons.get(level, '⚪')
        
        print(f"\n{icon} [{level}] {risk_type}")
        print(f"   Endpoint: {endpoint}")
        print(f"   CVSS: {cvss}")
        print(f"   Açıklama: {reasoning}")
    
    print("\n" + "=" * 60)


def display_vision_analysis(vision_results: Dict):
    """Vision analiz sonuçlarını göster"""
    results = vision_results.get('visual_analysis', [])
    
    if not results:
        print("ℹ️  Vision analizi sonucu yok")
        return
    
    # issues_found=true olanları filtrele
    issues = [r for r in results if r.get('issues_found')]
    
    if not issues:
        print("✅ Screenshot'larda görsel güvenlik sorunu tespit edilmedi!")
        return
    
    print("\n" + "=" * 60)
    print("👁️  GÖRSEL GÜVENLİK ANALİZİ")
    print("=" * 60)
    
    # Severity'ye göre sırala
    severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4}
    issues.sort(key=lambda x: severity_order.get(x.get('severity', 'Low'), 3))
    
    for idx, issue in enumerate(issues, 1):
        severity = issue.get('severity', 'Unknown')
        url = issue.get('url', 'N/A')
        desc = issue.get('description', 'No description')
        
        # Icon
        icons = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🔵', 'Info': '⚪'}
        icon = icons.get(severity, '⚪')
        
        print(f"\n{icon} [{severity}] Screenshot #{idx}")
        print(f"   URL: {url[:80]}")
        print(f"   Tespit: {desc}")
    
    print("\n" + "=" * 60)

def save_analysis(analysis, output_file):
    """Analizi dosyaya kaydet"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Analiz kaydedildi: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Kullanım:")
        print("  python analyze_with_ai.py scan-results.json")
        print("  python analyze_with_ai.py scan-results.json --model gpt-4o")
        print("  python analyze_with_ai.py scan-results.json --vision-only")
        sys.exit(1)
    
    # Parametreler
    scan_file = sys.argv[1]
    endpoint_model = "gpt-3.5-turbo"  # Endpoint analizi için (ucuz)
    vision_model = "gpt-4o-mini"      # Vision analizi için (maliyet-etkin)
    vision_only = '--vision-only' in sys.argv
    
    if '--model' in sys.argv:
        model_idx = sys.argv.index('--model')
        if len(sys.argv) > model_idx + 1:
            custom_model = sys.argv[model_idx + 1]
            endpoint_model = custom_model
            # Vision için o veya mini olmalı
            if 'gpt-4' in custom_model:
                vision_model = "gpt-4o" if "gpt-4o" in custom_model else "gpt-4o-mini"
    
    # OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable bulunamadı!")
        print("PowerShell'de şunu çalıştır:")
        print('   $env:OPENAI_API_KEY="sk-your-key-here"')
        sys.exit(1)
    
    # Scan sonuçlarını yükle
    print(f"📂 Dosya yükleniyor: {scan_file}")
    results = load_scan_results(scan_file)
    
    endpoints = results.get('endpoints', [])
    screenshots = results.get('screenshots', [])
    stats = results.get('statistics', {})
    
    print(f"✓ {len(endpoints)} endpoint")
    print(f"✓ {len(screenshots)} screenshot")
    print(f"✓ {stats.get('pages_crawled', 0)} sayfa taranmış\n")
    
    print("=" * 60)
    print("🤖 AI ANALİZİ (STRUCTURED OUTPUTS)")
    print("=" * 60)
    print()
    
    final_results = {}
    
    # 1. ENDPOINT ANALİZİ (vision-only değilse)
    if not vision_only and endpoints:
        endpoint_analysis = analyze_endpoints_with_ai(endpoints, api_key, endpoint_model)
        final_results['endpoint_analysis'] = endpoint_analysis
        display_endpoint_analysis(endpoint_analysis)
    
    # 2. VISION ANALİZİ (screenshot varsa)
    if screenshots:
        vision_analysis = analyze_screenshots_with_vision(screenshots, api_key, vision_model)
        final_results['vision_analysis'] = vision_analysis
        display_vision_analysis(vision_analysis)
    else:
        print("ℹ️  Screenshot bulunamadı - Vision analizi atlanıyor")
        print("   Screenshot almak için scan yaparken --capture-screenshots kullan\n")
    
    # Kaydet
    output_file = scan_file.replace('.json', '-ai-analysis.json')
    save_analysis(final_results, output_file)
    
    # ÖZET
    print("\n" + "=" * 60)
    print("📊 ANALİZ ÖZETİ")
    print("=" * 60)
    
    if 'endpoint_analysis' in final_results:
        ep_results = final_results['endpoint_analysis'].get('analysis', [])
        ep_risks = [r for r in ep_results if r.get('risk_detected')]
        critical = sum(1 for r in ep_risks if r.get('risk_level') == 'Critical')
        high = sum(1 for r in ep_risks if r.get('risk_level') == 'High')
        print(f"🎯 Endpoint: {len(ep_risks)} risk ({critical} Critical, {high} High)")
    
    if 'vision_analysis' in final_results:
        vis_results = final_results['vision_analysis'].get('visual_analysis', [])
        vis_issues = [r for r in vis_results if r.get('issues_found')]
        critical_vis = sum(1 for r in vis_issues if r.get('severity') == 'Critical')
        high_vis = sum(1 for r in vis_issues if r.get('severity') == 'High')
        print(f"👁️  Vision: {len(vis_issues)} sorun ({critical_vis} Critical, {high_vis} High)")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
