@echo off
setlocal
start "" "%~dp0editor\offline.html"
if errorlevel 1 echo Editor acilamadi. editor\offline.html dosyasini tarayicinizda acin.
endlocal
