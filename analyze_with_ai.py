"""
AI-Powered Endpoint Security Analyzer
OpenAI ile endpoint güvenlik analizi

Kullanım:
    python analyze_with_ai.py scan-www.lcw.com.json
    python analyze_with_ai.py scan-www.lcw.com.json --model gpt-4
"""

import json
import sys
import os
from openai import OpenAI

def load_scan_results(json_file):
    """Scan sonuçlarını yükle"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_endpoints_with_ai(endpoints, api_key, model="gpt-3.5-turbo"):
    """
    OpenAI ile endpoint'leri analiz et
    
    Ne tespit eder:
    - IDOR (Insecure Direct Object Reference)
    - BOLA (Broken Object Level Authorization)
    - SSRF potansiyeli
    - Mass Assignment
    - Authentication bypass
    """
    
    client = OpenAI(api_key=api_key)
    
    # Endpoint listesini hazırla
    endpoint_summary = []
    for ep in endpoints[:50]:  # İlk 50 endpoint (token limiti için)
        endpoint_summary.append({
            'method': ep['method'],
            'url': ep['url_template'],
            'parameters': [p['name'] for p in ep.get('parameters', [])]
        })
    
    # AI prompt
    prompt = f"""Sen bir güvenlik uzmanısın. Aşağıdaki API endpoint'lerini analiz et ve güvenlik açıklarını tespit et.

ENDPOINT LİSTESİ:
{json.dumps(endpoint_summary, indent=2)}

Şunları analiz et:
1. IDOR (Insecure Direct Object Reference) - userId, orderId gibi parametrelerle direkt nesne erişimi
2. BOLA (Broken Object Level Authorization) - Yetkilendirme eksikliği
3. SSRF - URL parametresi alan endpoint'ler
4. Mass Assignment - Çok fazla parametre alan POST/PUT endpoint'leri
5. Admin endpoint'leri - /admin, /internal gibi hassas path'ler

Her risk için:
- Endpoint URL'i
- Risk seviyesi (Critical/High/Medium/Low)
- Açıklama
- Test önerisi

JSON formatında yanıt ver:
{{
  "risks": [
    {{
      "endpoint": "DELETE /api/users/{{userId}}",
      "risk_level": "Critical",
      "vulnerability_type": "IDOR",
      "description": "userId parametresi ile başka kullanıcılar silinebilir",
      "test_recommendation": "Farklı userId değerleri ile DELETE isteği gönder",
      "cvss_score": 9.1
    }}
  ]
}}
"""
    
    print("🤖 AI analizi başlatılıyor...")
    print(f"📊 {len(endpoint_summary)} endpoint analiz ediliyor...")
    print(f"🔧 Model: {model}\n")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Sen bir API güvenlik uzmanısın. Endpoint'leri analiz edip güvenlik açıklarını tespit ediyorsun."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Daha deterministik sonuçlar
            max_tokens=2000
        )
        
        # Yanıtı parse et
        ai_response = response.choices[0].message.content
        
        # JSON parse et
        try:
            # Markdown code block'ları temizle
            if '```json' in ai_response:
                ai_response = ai_response.split('```json')[1].split('```')[0]
            elif '```' in ai_response:
                ai_response = ai_response.split('```')[1].split('```')[0]
            
            analysis = json.loads(ai_response.strip())
        except json.JSONDecodeError:
            # JSON parse edilemezse raw text dön
            analysis = {"raw_response": ai_response, "risks": []}
        
        return analysis
        
    except Exception as e:
        print(f"❌ AI analizi hatası: {e}")
        return {"error": str(e), "risks": []}

def display_analysis(analysis):
    """Analiz sonuçlarını göster"""
    if 'error' in analysis:
        print(f"❌ Hata: {analysis['error']}")
        return
    
    if 'raw_response' in analysis:
        print("\n📄 AI Yanıtı:")
        print(analysis['raw_response'])
        return
    
    risks = analysis.get('risks', [])
    
    if not risks:
        print("✅ Kritik güvenlik riski tespit edilmedi!")
        return
    
    print("\n" + "=" * 60)
    print("⚠️  TESPİT EDİLEN GÜVENLİK RİSKLERİ")
    print("=" * 60)
    
    # Risk seviyesine göre sırala
    risk_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    risks.sort(key=lambda x: risk_order.get(x.get('risk_level', 'Low'), 3))
    
    for idx, risk in enumerate(risks, 1):
        level = risk.get('risk_level', 'Unknown')
        vuln_type = risk.get('vulnerability_type', 'Unknown')
        endpoint = risk.get('endpoint', 'N/A')
        desc = risk.get('description', 'No description')
        test = risk.get('test_recommendation', 'No recommendation')
        cvss = risk.get('cvss_score', 'N/A')
        
        # Renk kodu
        color_map = {
            'Critical': '🔴',
            'High': '🟠',
            'Medium': '🟡',
            'Low': '🔵'
        }
        icon = color_map.get(level, '⚪')
        
        print(f"\n{icon} Risk #{idx} - {level}")
        print(f"   Endpoint: {endpoint}")
        print(f"   Tip: {vuln_type}")
        print(f"   CVSS Score: {cvss}")
        print(f"   Açıklama: {desc}")
        print(f"   Test: {test}")
    
    print("\n" + "=" * 60)

def save_analysis(analysis, output_file):
    """Analizi dosyaya kaydet"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Analiz kaydedildi: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Kullanım: python analyze_with_ai.py scan-results.json [--model gpt-4]")
        sys.exit(1)
    
    # Parametreler
    scan_file = sys.argv[1]
    model = "gpt-3.5-turbo"  # Varsayılan (ucuz)
    
    if '--model' in sys.argv:
        model_idx = sys.argv.index('--model')
        if len(sys.argv) > model_idx + 1:
            model = sys.argv[model_idx + 1]
    
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
    stats = results.get('statistics', {})
    
    print(f"✓ {len(endpoints)} endpoint yüklendi")
    print(f"✓ {stats.get('pages_crawled', 0)} sayfa taranmış\n")
    
    # AI analizi
    analysis = analyze_endpoints_with_ai(endpoints, api_key, model)
    
    # Sonuçları göster
    display_analysis(analysis)
    
    # Kaydet
    output_file = scan_file.replace('.json', '-ai-analysis.json')
    save_analysis(analysis, output_file)
    
    # Özet
    risks = analysis.get('risks', [])
    if risks:
        critical = sum(1 for r in risks if r.get('risk_level') == 'Critical')
        high = sum(1 for r in risks if r.get('risk_level') == 'High')
        print(f"\n📊 Özet: {critical} Critical, {high} High risk bulundu")

if __name__ == '__main__':
    main()
