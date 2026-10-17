@echo off
rem Saved captured ship only. Child-local full texture residency; never launches SFC.
"C:\Users\rober\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "%~dp0run_mesh_preview.py" --job C:/Project/RemixJobs/20261016-050350Z-6dffd5be --textures --resident-textures %*
if errorlevel 1 pause
