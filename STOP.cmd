@echo off
setlocal
cd /d "%~dp0"
set "HERMES_HOME=%~dp0home"

set "PY="
for /d %%d in (runtime\python\*) do if exist "%%d\python.exe" set "PY=%%d\python.exe"
if not defined PY (
  echo Could not find the runtime. Is this running from the stick root?
  timeout /t 3 /nobreak >nul 2>&1 || ping -n 4 127.0.0.1 >nul 2>&1
  exit /b 1
)

echo Stopping...
"%PY%" run.py gateway stop >nul 2>&1
echo Stopped. Safe to remove the stick.
timeout /t 2 /nobreak >nul 2>&1 || ping -n 3 127.0.0.1 >nul 2>&1
exit
