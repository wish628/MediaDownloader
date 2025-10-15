@echo off
echo Media Downloader Installer Creator
echo =================================
echo.

REM Check if Inno Setup is installed
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /? >nul 2>&1
if %errorlevel% NEQ 0 (
    "C:\Program Files\Inno Setup 6\ISCC.exe" /? >nul 2>&1
    if %errorlevel% NEQ 0 (
        echo Inno Setup 6 not found in the default installation directories.
        echo.
        echo Please install Inno Setup 6 from https://jrsoftware.org/isinfo.php
        echo.
        echo Make sure to install it in the default location:
        echo   - C:\Program Files (x86)\Inno Setup 6\ or
        echo   - C:\Program Files\Inno Setup 6\
        echo.
        echo After installation, run this script again.
        echo.
        pause
        exit /b 1
    )
)

echo Compiling installer...
echo.

REM Compile the installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "installer\MediaDownloader.iss" >nul 2>&1
if %errorlevel% NEQ 0 (
    "C:\Program Files\Inno Setup 6\ISCC.exe" "installer\MediaDownloader.iss" >nul 2>&1
    if %errorlevel% NEQ 0 (
        echo.
        echo Error: Failed to compile the installer.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo =================================
echo Installer created successfully!
echo.
echo The installer can be found in the installer\Output directory.
echo Installer file: MediaDownloader_v1.0.1_Installer.exe
echo.
echo Note: This installer includes the updated version with single instance protection and correct publisher information.
echo.
pause