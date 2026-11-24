@echo off
setlocal
set "SFC_PYTHON=C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%SFC_PYTHON%" (
  echo Development Python is missing. See the project development setup.
  exit /b 1
)
"%SFC_PYTHON%" -B "%~dp0run_source_session.py" --execute
if errorlevel 1 (
  echo Observation ended with an error. Exit SFC normally before trying again.
  pause
  exit /b 1
)
endlocal
