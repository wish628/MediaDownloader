@echo off
echo Compiling Media Downloader Installer...
echo.

REM Check if ISCC.exe is available
where ISCC.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: ISCC.exe (Inno Setup Compiler) not found.
    echo Please install Inno Setup 6 from https://jrsoftware.org/isinfo.php
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)

REM Compile the installer
ISCC.exe "MediaDownloader.iss"
if %errorlevel% neq 0 (
    echo Error: Failed to compile the installer.
    pause
    exit /b 1
)

echo.
echo Installer compiled successfully!
echo The installer can be found in the current directory.
echo.
pause