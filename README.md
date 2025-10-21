# Media Downloader

A powerful and user-friendly desktop application for downloading media from various online platforms.

![Media Downloader Interface](icon.ico)

## Table of Contents

- [Features](#features)
- [Supported Platforms](#supported-platforms)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Batch Downloading](#batch-downloading)
- [Playlist Support](#playlist-support)
- [Update Management](#update-management)
- [Notification System](#notification-system)
- [Download History](#download-history)
- [Troubleshooting](#troubleshooting)
- [Building from Source](#building-from-source)
- [Android Version](#android-version)
- [License](#license)

## Features

- **Multi-format Downloads**: Download videos and audio in various quality options
- **Batch Processing**: Download multiple URLs simultaneously
- **Playlist Support**: Select specific videos from playlists for download
- **User-Friendly Interface**: Intuitive GUI built with PyQt6
- **Progress Tracking**: Real-time download progress with speed and ETA
- **Pause/Resume**: Control downloads with pause and resume functionality
- **Error Handling**: Intelligent error classification and user-friendly messages
- **Update Management**: Automatic checking and updating of media engine
- **Notification System**: Desktop notifications for download events
- **Download History**: Track and manage your download history
- **Cross-Platform**: Works on Windows (with potential for macOS/Linux)

## Supported Platforms

Media Downloader supports downloading from a wide range of platforms including:

- YouTube
- Facebook
- Instagram
- TikTok
- Twitter
- Vimeo
- And hundreds more supported by yt-dlp

## Installation

### Windows

1. Download the latest installer from the [releases page](https://github.com/wish628/MediaDownloader/releases)
2. Run the installer and follow the setup wizard
3. Launch Media Downloader from your desktop or start menu

### System Requirements

- Windows 7 or later
- At least 100MB of free disk space
- Internet connection for downloading media

## Usage

1. Launch Media Downloader
2. Paste the URL of the media you want to download
3. Select the download type:
   - **Download Video**: Downloads video with both audio
   - **Download Audio**: Extracts and downloads audio only
   - **Download Playlist**: Downloads an entire playlist or selected videos
4. Click the appropriate download button
5. Monitor progress in the progress bar
6. Find your downloaded files in the specified output directory

### Interface Elements

- **URL Input**: Paste one or multiple URLs (one per line for batch downloads)
- **Download Buttons**: Choose video, audio, or playlist download
- **Output Directory**: Shows where files will be saved (click "Change Folder" to modify)
- **Progress Bar**: Visual indicator of download progress
- **Controls**: Pause, Resume, and Cancel buttons for active downloads
- **Settings**: Access configuration options
- **History**: View download history
- **Check Updates**: Manually check for media engine updates

## Configuration

Access settings through the "Settings" button in the top-right corner:

- **Video Quality**: Choose from Best, 1080p, 720p, 480p, or 360p
- **Audio Format**: Select output format (m4a, mp3, wav)
- **Max Retries**: Set number of retry attempts for failed downloads
- **Proxy Support**: Configure proxy settings if needed

Settings are automatically saved and persist between sessions.

## Batch Downloading

To download multiple files at once:

1. Paste multiple URLs in the text area (one per line)
2. Select either "Download Video" or "Download Audio"
3. The application will download all URLs concurrently (up to 3 simultaneous downloads)

## Playlist Support

When downloading playlists:

1. Paste the playlist URL and click "Download Playlist"
2. A dialog will appear showing all videos in the playlist
3. Select which videos you want to download
4. Click "Download Selected" to begin downloading

For automatic playlist detection, if you paste a playlist URL and select "Download Video" or "Download Audio", the application will detect it's a playlist and ask if you want to select specific videos or download the entire playlist.

## Update Management

Media Downloader uses yt-dlp as its media engine and automatically checks for updates:

- **Automatic Checks**: Updates are checked on application startup
- **Manual Checks**: Use the "Check Updates" button to manually check
- **One-Click Updates**: Update the media engine with a single click

## Notification System

The application provides desktop notifications for:

- Download completion
- Download errors
- Update availability
- Application events

Notifications can be viewed in the Notification Center accessible through the system tray.

## Download History

Track your downloads through the History feature:

- View all past downloads with status information
- Filter by successful downloads or errors
- Clear history when needed
- Double-click entries to open the download location

## Troubleshooting

Common issues and solutions:

### Download Fails
- Check your internet connection
- Verify the URL is correct and accessible
- Try a different quality setting
- Update the media engine through the update feature

### "FFmpeg Not Found" Error
- This should not occur with the installed version as ffmpeg is bundled
- If encountered, please report as a bug

### Slow Downloads
- Try a lower quality setting
- Check your internet connection speed
- Ensure no other bandwidth-intensive applications are running

### Proxy Issues
- Configure proxy settings in the Settings dialog
- Ensure proxy credentials are correct if required

## Building from Source

### Prerequisites

- Python 3.8 or later
- Required Python packages (see [requirements.txt](requirements.txt))

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/wish628/MediaDownloader.git
   cd MediaDownloader
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

### Creating an Installer

1. Install Inno Setup 6
2. Run [create_installer.bat](create_installer.bat) to create the Windows installer

## Android Version

Media Downloader is also available for Android devices. You can build the Android APK using GitHub Actions without needing Linux locally.

### Building the Android APK

1. Fork this repository or push it to your own GitHub account
2. GitHub Actions will automatically build the APK
3. Download the APK from the Actions tab

For detailed instructions, see [ANDROID_BUILD_INSTRUCTIONS.md](ANDROID_BUILD_INSTRUCTIONS.md).

### Features on Android

- Download videos and audio from supported platforms
- Simple and intuitive touch interface
- Download history tracking
- Settings customization
- Progress tracking with pause/resume support

### Requirements

- Android 5.0 (Lollipop) or higher
- At least 100MB of free storage space
- Internet connection for downloading media

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Media engine for downloading
- [PyQt6](https://pypi.org/project/PyQt6/) - GUI framework (Desktop)
- [Kivy](https://kivy.org/) - GUI framework (Android)
- [PyInstaller](https://pyinstaller.org/) - Application bundling (Desktop)
- [Buildozer](https://buildozer.readthedocs.io/) - APK building tool (Android)
- [FFmpeg](https://ffmpeg.org/) - Media processing (bundled)

---

**Note**: This application is for personal use only. Please respect the terms of service of the platforms you download from and only download content you have the right to access.