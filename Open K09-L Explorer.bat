@echo off
rem Double-click to open the K09-L Explorer (3-D model, decision, team, subsystems, simulations, status, docs).
rem It starts a small local web server for redesign\site and opens your browser. Close this window to stop it.
setlocal
cd /d "%~dp0redesign\site"
set PORT=8765

set PY=
where python >nul 2>nul && set PY=python
if not defined PY where py >nul 2>nul && set PY=py
if not defined PY goto nopython

echo Opening the K09-L Explorer at http://localhost:%PORT%/
echo Keep this window open while you use it. Close it to stop.
start "" "http://localhost:%PORT%/index.html#aircraft"
%PY% -m http.server %PORT% --bind 127.0.0.1
goto :eof

:nopython
echo Python was not found. Install it from https://www.python.org/downloads/ and run this again.
pause
