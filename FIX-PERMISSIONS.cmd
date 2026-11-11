@echo off
setlocal
set "ROOT=%~dp0"
set "TARGET=%ROOT%home"

net session >nul 2>&1
if %errorlevel% neq 0 (
  echo Requesting administrator rights...
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

echo.
echo  Fixing permissions on %TARGET%
echo  ---------------------------------------------
takeown /F "%TARGET%" /R /D Y >nul 2>&1
icacls "%TARGET%" /grant *S-1-1-0:(OI)(CI)F /T >nul 2>&1
rmdir /s /q "%TARGET%\gateway-locks" >nul 2>&1

echo  Done. Permissions reset, lock folder cleared.
echo.
echo  Close this window and double-click Invaderr.vbs normally.
echo  Do NOT run Invaderr as administrator.
echo.
pause
