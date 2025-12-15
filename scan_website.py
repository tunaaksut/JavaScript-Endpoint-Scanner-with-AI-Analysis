"""
Generic Website Scanner
Scan any website for API endpoints

Usage:
    python scan_website.py https://example.com
    python scan_website.py https://example.com --pages 50 --depth 4
"""

import asyncio
import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from runtime.crawl import RuntimeCrawler, CrawlConfig

async def scan_website(target_url, max_pages=30, max_depth=3, capture_screenshots=False):
    print("=" * 60)
    print("🔍 JS Endpoint Scanner")
    print("=" * 60)
    print(f"🎯 Target: {target_url}")
    print(f"📄 Max Pages: {max_pages}")
    print(f"🔗 Max Depth: {max_depth}")
    print(f"📸 Screenshots: {'Evet (Vision API)' if capture_screenshots else 'Hayır'}")
    print("=" * 60)
    print()
    
    # Configure crawler
    config = CrawlConfig(
        target_url=target_url,
        max_pages=max_pages,
        max_depth=max_depth,
        headless=True,
        simulate_user=True,  # (scroll/click simülasyonu)
        timeout_ms=30000,  # 30 saniye (120 saniye yerine)
        wait_for_network_idle=False,
        respect_robots_txt=True,
        capture_screenshots=capture_screenshots,  # Vision API için
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    crawler = RuntimeCrawler(config)
    
    try:
        print("🚀 Starting crawl...\n")
        results = await crawler.crawl()
        
        print("\n" + "=" * 60)
        print("📊 SCAN RESULTS")
        print("=" * 60)
        print(f"✓ Pages crawled: {results['statistics']['pages_crawled']}")
        print(f"✓ Network requests: {results['statistics']['network_requests']}")
        print(f"✓ Unique endpoints: {results['statistics']['unique_endpoints']}")
        print(f"✓ Screenshots: {results['statistics'].get('screenshots_captured', 0)}")
        print(f"✓ Duration: {results['statistics']['duration_ms']:.0f}ms")
        print()
        
        if results['endpoints']:
            print("=" * 60)
            print("🎯 DISCOVERED API ENDPOINTS")
            print("=" * 60)
            
            for idx, ep in enumerate(results['endpoints'][:30], 1):
                print(f"\n{idx}. {ep['method']:6} {ep['url_template']}")
                if ep.get('parameters'):
                    params = ', '.join([p['name'] for p in ep['parameters'][:5]])
                    if len(ep['parameters']) > 5:
                        params += f" ... (+{len(ep['parameters'])-5} more)"
                    print(f"   Parameters: {params}")
        
        # Generate output filename from URL
        domain = target_url.replace('https://', '').replace('http://', '').replace('/', '-').replace(':', '-')
        output_file = f'scan-{domain}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full results saved to: {output_file}")
        print("\n✅ Scan completed successfully!")
        
        # Return output file for AI analysis
        return output_file
        
    except Exception as e:
        print(f"\n❌ Scan failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        return None
        return None

def run_ai_analysis(scan_file, model="gpt-3.5-turbo", vision_only=False):
    """Run AI analysis on scan results"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("\n⚠️  OpenAI API key bulunamadı - AI analizi atlanıyor")
        print("   AI analizi için: $env:OPENAI_API_KEY=\"your-key\"")
        return
    
    print("\n" + "=" * 60)
    print("🤖 AI ANALİZİ BAŞLATILIYOR...")
    print("=" * 60)
    
    try:
        # analyze_with_ai.py'yi çalıştır
        import subprocess
        cmd = [sys.executable, 'analyze_with_ai.py', scan_file, '--model', model]
        if vision_only:
            cmd.append('--vision-only')
        
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print("⚠️  AI analizi tamamlanamadı")
    except Exception as e:
        print(f"⚠️  AI analizi hatası: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan website for API endpoints with AI analysis')
    parser.add_argument('url', help='Target URL (e.g., https://example.com)')
    parser.add_argument('--pages', type=int, default=10, help='Max pages to crawl (default: 10)')
    parser.add_argument('--depth', type=int, default=2, help='Max crawl depth (default: 2)')
    parser.add_argument('--screenshots', action='store_true', help='Capture screenshots for Vision API analysis')
    parser.add_argument('--no-ai', action='store_true', help='Skip AI analysis (only scan)')
    parser.add_argument('--ai-model', type=str, default='gpt-3.5-turbo', help='AI model (gpt-3.5-turbo, gpt-4, gpt-4o)')
    parser.add_argument('--vision-only', action='store_true', help='Only run Vision analysis (skip endpoint analysis)')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith('http'):
        print("❌ Error: URL must start with http:// or https://")
        sys.exit(1)
    
    # Run scan
    output_file = asyncio.run(scan_website(args.url, args.pages, args.depth, args.screenshots))
    
    # Run AI analysis (unless --no-ai flag is set)
    if not args.no_ai and output_file:
        run_ai_analysis(output_file, args.ai_model, args.vision_only)
