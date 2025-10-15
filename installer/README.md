# Media Downloader Installer

This directory contains the files needed to create an installer for the Media Downloader application.

## Prerequisites

1. Inno Setup 6 must be installed on your system
   - Download from: https://jrsoftware.org/isinfo.php
   - Install with default settings

## Creating the Installer

### Method 1: Using the Batch File (Windows)

1. Double-click on [compile_installer.bat](file://c:\Users\hp\Desktop\yt1\installer\compile_installer.bat) to compile the installer
2. The installer will be created in this directory

### Method 2: Using Command Line

1. Open Command Prompt
2. Navigate to this directory
3. Run the following command:
   ```
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" MediaDownloader.iss
   ```

### Method 3: Using Inno Setup IDE

1. Open Inno Setup IDE
2. Open the [MediaDownloader.iss](file://c:\Users\hp\Desktop\yt1\installer\MediaDownloader.iss) file
3. Click "Build" from the menu

## Output

The installer will be created as `MediaDownloader_v1.0.1_Installer.exe` in this directory.

## Customization

You can modify the following parameters in the [MediaDownloader.iss](file://c:\Users\hp\Desktop\yt1\installer\MediaDownloader.iss) file:

- `MyAppVersion`: Application version
- `MyAppPublisher`: Publisher name
- `MyAppURL`: Application URL