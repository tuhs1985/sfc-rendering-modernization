@echo off
rem Explicit hypothesis viewer only; normal textured/grey launchers remain unchanged.
"C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "%~dp0run_mesh_preview.py" --job C:/Project/RemixJobs/20261016-050350Z-6dffd5be --textures --resident-textures --provisional-lighting %*
if errorlevel 1 pause
