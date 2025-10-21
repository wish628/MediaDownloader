# Building Android APK with GitHub Actions

This guide explains how to build an Android APK for the Media Downloader application using GitHub Actions, without needing Linux or WSL locally.

## Prerequisites

1. A GitHub account
2. Git installed on your Windows machine

## Steps to Build Your APK

### 1. Create a GitHub Repository

1. Go to [github.com](https://github.com) and log in
2. Click the "+" icon and select "New repository"
3. Name your repository (e.g., "MediaDownloader")
4. Choose public or private
5. Click "Create repository"

### 2. Push Your Code to GitHub

Open Git Bash or Command Prompt in your project directory and run:

```bash
git init
git add .
git commit -m "Initial commit for Android APK"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPOSITORY_NAME` with your actual GitHub username and repository name.

### 3. Monitor the Build Process

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. You should see the "Build Android APK" workflow running
4. Click on it to see detailed logs

### 4. Download Your APK

1. After the build completes successfully, scroll down to the "Artifacts" section
2. Click on "mediadownloader-apk" to download a ZIP file containing your APK
3. Extract the ZIP file to get your APK

## Troubleshooting

### Build Fails

If the build fails:
1. Check the logs in the Actions tab for error messages
2. Common issues:
   - Missing dependencies in requirements.txt
   - Incorrect file paths in buildozer.spec
   - Network issues during dependency downloads

### First Build Takes Long

The first build will take 30-60 minutes as it downloads:
- Android NDK
- Android SDK
- All Python dependencies
- Other build tools

Subsequent builds will be faster due to caching.

## Manual Trigger

You can manually trigger a build:
1. Go to the "Actions" tab in your repository
2. Click on "Build Android APK" in the left sidebar
3. Click "Run workflow" and then "Run workflow"

## Customizing the Build

### Changing App Name or Package

Edit [buildozer.spec](file:///c%3A/Users/hp/Desktop/yt1/buildozer.spec):
```ini
[app]
title = Your App Name
package.name = yourappname
package.domain = com.yourdomain
```

### Adding Permissions

Edit [buildozer.spec](file:///c%3A/Users/hp/Desktop/yt1/buildozer.spec):
```ini
[app]
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
```

## Signing Your APK for Release

To create a signed release APK:

1. Generate a keystore (run on any machine with Java):
   ```bash
   keytool -genkey -v -keystore release.keystore -alias androidkey -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Convert to base64:
   ```bash
   base64 -i release.keystore -o keystore.txt
   ```

3. Add as a secret in your GitHub repository:
   - Go to your repository settings
   - Click "Secrets and variables" → "Actions"
   - Click "New repository secret"
   - Name: `ANDROID_KEYSTORE_B64`
   - Value: Contents of keystore.txt

The workflow will automatically sign your APK when this secret is present.

## APK Installation

To install the APK on your Android device:

1. Enable "Install from unknown sources" in your device settings
2. Transfer the APK to your device
3. Tap on the APK file to install

## Limitations

1. GitHub Actions has a 6-hour timeout for free accounts
2. Builds use Ubuntu runners with limited resources
3. Large apps might exceed storage limits

For more information, see the [GitHub Actions documentation](https://docs.github.com/en/actions).