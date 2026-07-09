@echo off
chcp 65001 >nul 2>&1
title Gongyuan Film Simulator Launcher
cd /d "%~dp0"

set "PY_EXE="
set "PY_ARGS="

echo(
echo( ================================================================
echo(     Gongyuan Film Museum - Digital Darkroom v2.0
echo( ================================================================
echo(

REM ============ Find python.exe pure path + separate args ============
where python >nul 2>&1
if errorlevel 1 goto s2
for /f "delims=" %%i in ('where python 2^>nul') do (
    "%%i" -c "import sys; sys.exit(0)" >nul 2>&1
    if not errorlevel 1 (
        set "PY_EXE=%%i"
        goto found
    )
)

:s2
where py >nul 2>&1
if errorlevel 1 goto s3
for /f "delims=" %%i in ('where py 2^>nul') do (
    "%%i" -3 -c "import sys; sys.exit(0)" >nul 2>&1
    if not errorlevel 1 (
        set "PY_EXE=%%i"
        set "PY_ARGS=-3"
        goto found
    )
)

:s3
echo(   Not in PATH. Checking typical Python install folders...
echo(

call :try "%%LocalAppData%%\Programs\Python\Python313\python.exe"
if defined PY_EXE goto found
call :try "%%LocalAppData%%\Programs\Python\Python312\python.exe"
if defined PY_EXE goto found
call :try "%%LocalAppData%%\Programs\Python\Python311\python.exe"
if defined PY_EXE goto found
call :try "%%LocalAppData%%\Programs\Python\Python310\python.exe"
if defined PY_EXE goto found
call :try "%%LocalAppData%%\Programs\Python\Python39\python.exe"
if defined PY_EXE goto found
call :try "C:\Program Files\Python313\python.exe"
if defined PY_EXE goto found
call :try "C:\Program Files\Python312\python.exe"
if defined PY_EXE goto found
call :try "C:\Program Files\Python311\python.exe"
if defined PY_EXE goto found
call :try "C:\Program Files\Python310\python.exe"
if defined PY_EXE goto found
call :try "C:\Program Files\Python39\python.exe"
if defined PY_EXE goto found
call :try "C:\Python311\python.exe"
if defined PY_EXE goto found
call :try "C:\Python310\python.exe"
if defined PY_EXE goto found

if exist "C:\Windows\py.exe" (
    "C:\Windows\py.exe" -3 -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        set "PY_EXE=C:\Windows\py.exe"
        set "PY_ARGS=-3"
        goto found
    )
)

REM ============ Manual fallback ============
:s4
echo(
echo( ============================================================
echo(   [Auto-detect failed]
echo( ============================================================
echo(
echo(   Option A [you already have Python somewhere]:
echo(     In File Explorer, search "python.exe" on C:,
echo(     then DRAG it with your mouse INTO this window + press ENTER.
echo(
echo(   Option B [Python is NOT installed]:
echo(     1. URL: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
echo(     2. Installer first screen TICK: [x] Add Python.exe to PATH
echo(     3. Reopen this bat after install.
echo(
:ask
set "PY_EXE="
set /p "PY_EXE=   Drag python.exe here and press Enter, or paste full path: "
if "%PY_EXE%"=="" goto ask
set "PY_EXE=%PY_EXE:"=%"
if not exist "%PY_EXE%" ( echo(   File not found. & pause & goto ask )
"%PY_EXE%" -c "import sys" >nul 2>&1
if errorlevel 1 ( echo(   Invalid python. & pause & goto ask )
set "PY_ARGS="
goto found

:try
if exist %1 (
    %1 -c "import sys" >nul 2>&1
    if not errorlevel 1 set "PY_EXE=%~1"
)
exit /b

:found
echo(   Step 1/5 - Python interpreter found
echo(   EXE    : %PY_EXE%
if not "%PY_ARGS%"=="" echo(   ARGS   : %PY_ARGS%
for /f "delims=" %%v in ('"%PY_EXE%" %PY_ARGS% -c "import sys;print(sys.version.split()[0])" 2^>nul') do echo(   Version: %%v
echo(

REM ============ Dependencies ============
cd backend
echo(   Step 2/5 - Checking dependencies ...
"%PY_EXE%" %PY_ARGS% -c "import fastapi,uvicorn,PIL,cv2,numpy,multipart" >nul 2>&1
if errorlevel 1 goto install_deps
echo(           All present. Skipping install.
goto deps_ok

:install_deps
echo(           Installing ALL requirements from requirements.txt
echo(           (1-3 min via Tsinghua mirror, SAME interpreter)
echo(
"%PY_EXE%" %PY_ARGS% -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt
if errorlevel 1 (
    echo(
    echo(   [ERROR] Dependency install FAILED.
    echo(     * Check internet connection
    echo(     * Or run: "%PY_EXE%" %PY_ARGS% -m pip install --upgrade pip
    echo(     * Or right-click bat - Run as Administrator
    echo(     * Screenshot any error text and send it to me
    echo(
    pause
    exit /b 2
)
echo(           Install finished.

:deps_ok
echo(
echo(   Step 3/5 - Self-test: load 8-film library
echo(
"%PY_EXE%" %PY_ARGS% -c "from film_library import FILMS; print(f'           Loaded {len(FILMS)} films:'); [print(f'             - {f[\"short_name\"]}') for f in FILMS.values()]"
if errorlevel 1 (
    echo(   [ERROR] Film library failed. See above.
    pause
    exit /b 3
)

echo(
echo(   Step 4/5 - Create output folders
if not exist uploads mkdir uploads
if not exist outputs mkdir outputs
if not exist test_outputs mkdir test_outputs
echo(           Ready.

echo(
echo( ================================================================
echo(   Step 5/5 - Start HTTP server
echo(
echo(   WEB UI       :  http://localhost:8000/
echo(   API DOCS     :  http://localhost:8000/docs
echo(   HEALTH CHECK :  http://localhost:8000/api/health
echo(   FILM LIST    :  http://localhost:8000/api/films
echo(
echo(   Browser opens in 3 seconds. LAN IPs printed in server log below.
echo(   Close this window to STOP the server.
echo( ================================================================
echo(

ping -n 4 127.0.0.1 >nul 2>&1
start "" "http://localhost:8000/"

echo(   Server log:
echo(   -----------------------------------------------------------------
"%PY_EXE%" %PY_ARGS% main.py

echo(
echo(   Server exited. If it crashed, screenshot above.
echo(
pause
