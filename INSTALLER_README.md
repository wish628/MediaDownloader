# Media Downloader Installer Creation

This document explains how to create an installer for the Media Downloader application.

## Prerequisites

1. Inno Setup 6 must be installed on your system
   - Download from: https://jrsoftware.org/isinfo.php
   - Install with default settings

## Creating the Installer

### Method 1: Using the Batch File (Recommended)

1. Double-click on [create_installer.bat](file://c:\Users\hp\Desktop\yt1\create_installer.bat) in the root directory
2. The installer will be created in the `installer\Output` directory

### Method 2: Manual Compilation

1. Open Command Prompt
2. Navigate to the project directory
3. Run the following command:
   ```
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "installer\MediaDownloader.iss"
   ```

### Method 3: Using Inno Setup IDE

1. Open Inno Setup IDE
2. Open the `installer\MediaDownloader.iss` file
3. Click "Build" from the menu

## Output

The installer will be created as `MediaDownloader_v1.0.1_Installer.exe` in the `installer\Output` directory.

## Directory Structure

```
project_root/
├── dist/
│   └── MediaDownloader_v1.0.1.exe     # Main executable
├── installer/
│   ├── MediaDownloader.iss            # Inno Setup script
│   ├── README.md                      # Installer documentation
│   ├── compile_installer.bat          # Batch file for compilation
│   └── Output/                        # Installer output directory
├── icon.ico                           # Application icon
├── create_installer.bat               # Main batch file (root directory)
└── INSTALLER_README.md                # This file
```

## Customization

You can modify the following parameters in the `installer\MediaDownloader.iss` file:

- `MyAppVersion`: Application version
- `MyAppPublisher`: Publisher name
- `MyAppURL`: Application URL