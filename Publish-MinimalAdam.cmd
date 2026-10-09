@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\publish-github.ps1"
if errorlevel 1 (
 echo.
 echo Yayin basarisiz oldu. Yukaridaki hata mesajini inceleyin.
 pause
 exit /b 1
)
echo.
echo Basarili. https://github.com/seydivakkas/MinimalAdam
pause
