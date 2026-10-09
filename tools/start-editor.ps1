$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$offline = Join-Path $root 'editor\offline.html'
if (!(Test-Path $offline)) { throw "Editor bulunamadı: $offline" }
Start-Process $offline
Write-Host "MinimalAdam Studio yerel HTML dosyasi aciliyor: $offline"
