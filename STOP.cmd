@echo off
setlocal
cd /d "%~dp0"
set "HERMES_HOME=%~dp0home"

set "PY="
for /d %%d in (runtime\python\*) do if exist "%%d\python.exe" set "PY=%%d\python.exe"
if not defined PY (
  echo Could not find the runtime. Is this running from the stick root?
  pause
  exit /b 1
)

echo Stopping the gateway...
"%PY%" run.py gateway stop

echo.
echo Done. You can remove the stick now.
pause
