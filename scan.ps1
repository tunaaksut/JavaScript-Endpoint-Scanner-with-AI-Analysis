# Quick Scan Script
# Drag & drop kullanımı için

param(
    [Parameter(Mandatory=$true)]
    [string]$Url,
    
    [int]$Pages = 30,
    [int]$Depth = 3
)

$pythonPath = "C:/Users/Tuna/Desktop/JavaScriptEndpoint/.venv/Scripts/python.exe"
$scriptPath = "C:/Users/Tuna/Desktop/JavaScriptEndpoint/scan_website.py"

Write-Host "🚀 Starting scan..." -ForegroundColor Green
Write-Host "📍 Target: $Url" -ForegroundColor Cyan
Write-Host "📄 Max pages: $Pages" -ForegroundColor Cyan
Write-Host ""

& $pythonPath $scriptPath $Url --pages $Pages --depth $Depth

Write-Host "`n✅ Scan complete!" -ForegroundColor Green
