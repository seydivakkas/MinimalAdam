# MinimalAdam v0.6 - Windows Codex installation
# Installs a separate skill; does not modify the original skill.
$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $packageRoot 'minimaladam'
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$skillsRoot = Join-Path $codexRoot 'skills'
$target = Join-Path $skillsRoot 'minimaladam'

if (-not (Test-Path (Join-Path $source 'SKILL.md'))) {
    throw 'Kaynak SKILL.md dosyasi bulunamadi.'
}
if (Test-Path $target) {
    throw "Hedef klasor mevcut: $target . Guvenlik icin var olan becerinin uzerine yazilmadi."
}
New-Item -ItemType Directory -Force -Path $skillsRoot | Out-Null
Copy-Item -Path $source -Destination $target -Recurse
Write-Host "Turkce beceri kuruldu: $target"
Write-Host 'Codex icinde $minimaladam kullanabilirsiniz.'
