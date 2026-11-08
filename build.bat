@echo off
rem ZERO DAY - builds the game folder dist\ZeroDay: ZeroDay.exe plus real lang, missions and sounds folders next to it.
rem Needs Python 3.10-3.12 for Windows from python.org (tick "Add Python to PATH"). Internet needed the first time.
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% --version >nul 2>nul
if errorlevel 1 goto :nopy

echo [1/4] Creating build environment...
if not exist .venv-build\Scripts\python.exe %PY% -m venv .venv-build
if errorlevel 1 goto :fail
set "VPY=.venv-build\Scripts\python.exe"

echo [2/4] Installing wxPython, pygame and PyInstaller...
%VPY% -m pip install --upgrade pip
%VPY% -m pip install wxPython pygame pyinstaller
if errorlevel 1 goto :fail
echo Installing optional screen reader support...
%VPY% -m pip install accessible-output2 >nul 2>nul
set "AO="
%VPY% -c "import accessible_output2" >nul 2>nul
if not errorlevel 1 set "AO=--collect-all accessible_output2"

echo [3/4] Building the program...
if not exist lang mkdir lang
if not exist sounds mkdir sounds
if not exist missions mkdir missions
set "ICON="
if exist icon.ico set "ICON=--icon icon.ico"
%VPY% -m PyInstaller --noconfirm --clean --onedir --windowed --name ZeroDay %ICON% %AO% gui.py
if errorlevel 1 goto :fail

echo [4/4] Copying lang, missions, sounds and the readme next to ZeroDay.exe...
xcopy /E /I /Y /Q lang "dist\ZeroDay\lang" >nul
xcopy /E /I /Y /Q missions "dist\ZeroDay\missions" >nul
xcopy /E /I /Y /Q sounds "dist\ZeroDay\sounds" >nul
copy /Y README.txt "dist\ZeroDay\README.txt" >nul
copy /Y LICENSE "dist\ZeroDay\LICENSE.txt" >nul
if errorlevel 1 goto :fail
echo.
echo   Your game folder: %~dp0dist\ZeroDay
echo   Copy or zip the WHOLE folder. Keep ZeroDay.exe together with the lang, missions and sounds folders next to it.
echo   To change a language or a mission, edit the files in those folders. Building again replaces dist\ZeroDay, so keep your edits in the folders next to build.bat.
echo   Notes and history are saved in your user folder.
echo.
pause
exit /b 0

:nopy
echo Python 3 was not found. Install it from https://www.python.org and tick "Add Python to PATH", then run this file again.
pause
exit /b 1

:fail
echo.
echo Build failed. Read the messages above. If wxPython could not be installed, use Python 3.11 or 3.12.
pause
exit /b 1
