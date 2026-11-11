@echo off
setlocal
set "ROOT=%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
  echo Requesting administrator rights...
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

echo.
echo  Repairing USB permissions
echo  ---------------------------------------------
echo  Removing the poisoned lock folder (the fix that works)...
powershell -NoProfile -Command "Remove-Item -Force -Recurse -ErrorAction SilentlyContinue '%ROOT%home\gateway-locks'"

echo  Resetting ownership on the home folder so it works on any PC...
icacls "%ROOT%home" /grant *S-1-1-0:(OI)(CI)F /T >nul 2>&1

echo.
echo  Done. Close this window and double-click Invaderr.vbs normally.
echo  Do NOT run Invaderr as administrator.
echo.
pause
