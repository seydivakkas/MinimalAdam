# MinimalAdam: mevcut GitHub deposuna guvenli ilk yayin
# Git Windows Credential Manager / GitHub tarayici oturumu gerekli olabilir.
param(
    [string]$RemoteUrl = 'https://github.com/seydivakkas/MinimalAdam.git'
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
function Run([string]$Label, [string]$Executable, [string[]]$Arguments) {
    Write-Host "`n==> $Label" -ForegroundColor Cyan
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Label basarisiz (cikis kodu: $LASTEXITCODE)." }
}
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git bulunamadi. https://git-scm.com/download/win adresinden Git for Windows kurun.'
}
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'Python bulunamadi. Once Python kurun veya paketin README dosyasini inceleyin.'
}
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    throw 'Node.js bulunamadi. CI testleriyle ayni JS kontrolleri icin Node 22+ gerekli.'
}
Run -Label 'Python paketlerini kur' -Executable 'python' -Arguments @('-m','pip','install','-r','requirements.txt')
Run -Label 'Python testleri' -Executable 'python' -Arguments @('-m','unittest','discover','-s','tests','-p','test_*.py','-q')
Run -Label 'JavaScript testleri' -Executable 'node' -Arguments @('--test','tests/js/p4_core.test.mjs','tests/js/p5_quality.test.mjs')
Run -Label 'Paket dogrulamasi' -Executable 'python' -Arguments @('tools/validate-package.py')
Run -Label 'P4 dogrulamasi' -Executable 'python' -Arguments @('tools/validate_p4.py')
Run -Label 'P5 dogrulamasi' -Executable 'python' -Arguments @('tools/validate_p5.py')
if (!(Test-Path .git)) { Run -Label 'Yeni Git deposu' -Executable 'git' -Arguments @('init','-b','main') }
$remotes = @(& git remote)
if ('origin' -notin $remotes) {
    Run -Label 'Origin ekle' -Executable 'git' -Arguments @('remote','add','origin',$RemoteUrl)
} elseif ((& git remote get-url origin).Trim() -ne $RemoteUrl) {
    throw "origin baska depoyu gosteriyor. Islem durduruldu."
}
Run -Label 'Dal adi main' -Executable 'git' -Arguments @('branch','-M','main')
Run -Label 'Dosyalari stage et' -Executable 'git' -Arguments @('add','-A')
& git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    Run -Label 'Surumu commit et' -Executable 'git' -Arguments @('commit','-m','feat: publish MinimalAdam v0.6.1 source, editor and CI')
} else {
    Write-Host 'Yeni degisiklik bulunamadi.'
}
# Force push asla kullanma; depo baskasi tarafindan degistiyse guvenli bicimde durdur.
Run -Label 'GitHub uzerine push' -Executable 'git' -Arguments @('push','-u','origin','main')
Write-Host "`nGitHub: https://github.com/seydivakkas/MinimalAdam" -ForegroundColor Green
Write-Host 'Windows CI icin GitHub -> Actions -> Windows acceptance kontrol edin.'
