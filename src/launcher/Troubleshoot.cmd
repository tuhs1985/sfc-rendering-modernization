@echo off
setlocal DisableDelayedExpansion
"%~dp0launcher.exe" --troubleshoot
set "SFC_LAUNCH_EXIT=%ERRORLEVEL%"
if not "%SFC_LAUNCH_EXIT%"=="0" pause
exit /b %SFC_LAUNCH_EXIT%
