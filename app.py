import sys
import os
import json
import datetime
import subprocess
import time
import requests
import yt_dlp
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QProgressBar, QFileDialog,
    QMessageBox, QDialog, QFormLayout, QComboBox, QCheckBox,
    QSpinBox, QMenu, QMenuBar, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QStackedWidget, QSystemTrayIcon, QMenu as QTrayMenu
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtNetwork import QLocalSocket, QLocalServer
from PyQt6.QtGui import QIcon, QAction # For application icon

# --- Update Checker Utility ---
class UpdateChecker:
    YT_DLP_VERSION_URL = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
    APP_VERSION = "1.0.1"  # Updated application version
    APP_VERSION_URL = "https://api.github.com/repos/wish628/MediaDownloader/releases/latest"  # GitHub repository URL
    
    @staticmethod
    def get_yt_dlp_version():
        """Get the currently installed yt-dlp version"""
        try:
            # Try to get version using yt_dlp module
            import yt_dlp
            version = getattr(yt_dlp, '__version__', None)
            if version:
                return version
        except:
            pass
        
        # Fallback to command line
        try:
            result = subprocess.run([sys.executable, '-m', 'yt_dlp', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
            
        # If all methods fail, return a more user-friendly message
        return 'unknown'

    @staticmethod
    def check_yt_dlp_update():
        """Check if there's a newer version of the media engine available"""
        try:
            current_version = UpdateChecker.get_yt_dlp_version()
            if current_version == 'unknown':
                return {
                    'status': 'error', 
                    'message': 'We couldn\'t detect your current media engine version. This might be because:\n\n'
                              '• The media engine isn\'t properly installed\n'
                              '• There\'s a network connectivity issue\n'
                              '• Your system configuration is preventing version detection\n\n'
                              'To resolve this:\n'
                              '1. Make sure the media engine is correctly installed\n'
                              '2. Check your internet connection\n'
                              '3. Try restarting the application\n'
                              '4. If problems persist, consider reinstalling the application'
                }
            
            # Fetch latest version info from GitHub
            response = requests.get(UpdateChecker.YT_DLP_VERSION_URL, timeout=10)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')  # Remove 'v' prefix
            
            # Compare versions
            if UpdateChecker._is_version_newer(latest_version, current_version):
                return {
                    'status': 'update_available',
                    'current_version': current_version,
                    'latest_version': latest_version,
                    'release_notes': latest_release.get('body', 'No release notes available'),
                    'download_url': latest_release.get('html_url', '')
                }
            else:
                return {
                    'status': 'up_to_date',
                    'current_version': current_version,
                    'latest_version': latest_version
                }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'error', 
                'message': 'We couldn\'t check for updates due to a network issue:\n\n'
                          f'• {str(e)}\n\n'
                          'To resolve this:\n'
                          '1. Check your internet connection\n'
                          '2. Verify that you can access github.com\n'
                          '3. If you\'re using a proxy, configure it in Settings\n'
                          '4. Try again in a few minutes'
            }
        except Exception as e:
            return {
                'status': 'error', 
                'message': 'We encountered an unexpected issue while checking for updates:\n\n'
                          f'• {str(e)}\n\n'
                          'To resolve this:\n'
                          '1. Try checking for updates again\n'
                          '2. Restart the application\n'
                    
                          '3. If the problem continues, check your network connection'
            }
    
    @staticmethod
    def update_yt_dlp():
        """Attempt to update the media engine"""
        try:
            # Try using pip to update the media engine
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return {
                    'status': 'success', 
                    'message': 'Great news! The media engine has been successfully updated.\n\n'
                              'To use the new version:\n'
                              '1. Please restart this application\n'
                              '2. Your downloads will now benefit from the latest improvements and bug fixes'
                }
            else:
                return {
                    'status': 'error', 
                    'message': 'We couldn\'t update the media engine automatically. This might be because:\n\n'
                              '• You need administrator privileges\n'
                              '• There\'s a network connectivity issue\n'
                              '• Your Python/pip installation has issues\n\n'
                              'To resolve this:\n'
                              '1. Try running this application as administrator\n'
                              '2. Manually update by running "pip install --upgrade yt-dlp" in your command prompt\n'
                              '3. Check your internet connection\n'
                              f'4. Error details: {result.stderr}'
                }
        except Exception as e:
            return {
                'status': 'error', 
                'message': 'We encountered an unexpected issue while trying to update the media engine:\n\n'
                          f'• {str(e)}\n\n'
                          'To resolve this:\n'
                          '1. Try updating again\n'
                          '2. Manually update by running "pip install --upgrade yt-dlp" in your command prompt\n'
                          '3. Restart the application'
            }
    
    @staticmethod
    def check_app_update():
        """Check if there's a newer version of the application available"""
        try:
            # Fetch latest version info from GitHub (replace with actual URL)
            response = requests.get(UpdateChecker.APP_VERSION_URL, timeout=10)
            if response.status_code == 404:
                # Repository not found, assume up to date
                return {
                    'status': 'up_to_date',
                    'current_version': UpdateChecker.APP_VERSION,
                    'message': 'No update information available'
                }
            
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')  # Remove 'v' prefix
            
            # Compare versions
            if UpdateChecker._is_version_newer(latest_version, UpdateChecker.APP_VERSION):
                return {
                    'status': 'update_available',
                    'current_version': UpdateChecker.APP_VERSION,
                    'latest_version': latest_version,
                    'release_notes': latest_release.get('body', 'No release notes available'),
                    'download_url': latest_release.get('html_url', '')
                }
            else:
                return {
                    'status': 'up_to_date',
                    'current_version': UpdateChecker.APP_VERSION,
                    'latest_version': latest_version
                }
        except Exception as e:
            return {'status': 'error', 'message': f'Failed to check for app updates: {str(e)}'}
    
    @staticmethod
    def _is_version_newer(new_version, current_version):
        """Compare two version strings"""
        try:
            # Simple version comparison (works for most semantic versions)
            new_parts = [int(x) for x in new_version.split('.')]
            current_parts = [int(x) for x in current_version.split('.')]
            
            for new, current in zip(new_parts, current_parts):
                if new > current:
                    return True
                elif new < current:
                    return False
            # If all parts compared equal, check if new version has more parts
            return len(new_parts) > len(current_parts)
        except:
            # Fallback to string comparison
            return new_version > current_version

# --- Update Dialog ---
class UpdateDialog(QDialog):
    def __init__(self, update_info, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.setWindowTitle("Update Available")
        self.setModal(True)
        self.resize(500, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Update Available")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Update info
        info_text = f"Current version: {update_info['current_version']}\n"
        info_text += f"Latest version: {update_info['latest_version']}\n\n"
        info_text += "Release notes:\n"
        info_text += update_info.get('release_notes', 'No release notes available')[:500] + "..."
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("margin-bottom: 15px;")
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        update_button = QPushButton("Update Now")
        later_button = QPushButton("Later")
        skip_button = QPushButton("Skip This Version")
        
        update_button.clicked.connect(self.accept)
        later_button.clicked.connect(self.reject)
        skip_button.clicked.connect(self.skip_version)
        
        button_layout.addWidget(update_button)
        button_layout.addWidget(later_button)
        button_layout.addWidget(skip_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def skip_version(self):
        # We could implement version skipping logic here
        self.reject()

# --- Error Handling Utility ---
class ErrorClassifier:
    @staticmethod
    def classify_error(error_message):
        """Classify errors into categories with user-friendly messages"""
        error_message = str(error_message).lower()
        
        # File system errors (check first to avoid conflicts)
        if any(keyword in error_message for keyword in ['permission', 'access denied', 'disk', 'space', 'read-only', 'no space', 'cannot create', 'directory not found']):
            return {
                'category': 'File System Access Issue',
                'message': 'We couldn\'t save the file to your selected location.',
                'suggestion': 'Check if you have write permissions to the download folder and ensure there\'s enough disk space. Try selecting a different download directory in Settings.'
            }
        
        # Invalid URL errors - More specific patterns for invalid URLs
        # Check for extractor-related errors first (before format errors)
        if any(keyword in error_message for keyword in ['no suitable extractor', 'unable to extract', 'this video is unavailable', 'infoextractor']):
            return {
                'category': 'Invalid or Unsupported Link',
                'message': 'The link you provided doesn\'t seem to be valid or isn\'t supported by our downloader.',
                'suggestion': 'Please double-check the URL and make sure it\'s from a supported platform. Sometimes links expire, get removed, or are mistyped.'
            }
        
        # Format/codec errors (but not extractor-related)
        if any(keyword in error_message for keyword in ['ffmpeg', 'codec', 'format', 'unsupported format']) and 'extractor' not in error_message:
            return {
                'category': 'Media Processing Issue',
                'message': 'We had trouble processing this media format.',
                'suggestion': 'Try changing the download format in Settings. Some formats may not be compatible with your system.'
            }
        
        # Invalid URL errors - Basic patterns
        if any(keyword in error_message for keyword in ['invalid url', 'unsupported url', 'not found', '404', 'not a valid url']):
            return {
                'category': 'Invalid or Unsupported Link',
                'message': 'The link you provided doesn\'t seem to be valid or isn\'t supported by our downloader.',
                'suggestion': 'Please double-check the URL and make sure it\'s from a supported platform. Sometimes links expire, get removed, or are mistyped.'
            }
        
        # Authentication errors
        if any(keyword in error_message for keyword in ['login', 'authentication', 'signin', 'forbidden', '403', 'private', 'age-restricted']):
            return {
                'category': 'Access Restricted Content',
                'message': 'This content requires special permissions or login credentials.',
                'suggestion': 'The video might be private, age-restricted, or region-blocked. Try logging into the platform directly first, or check if you have the necessary permissions.'
            }
        
        # Network errors
        if any(keyword in error_message for keyword in ['timeout', 'network', 'connection', 'unreachable', 'dns', 'resolve', 'internet', 'getaddrinfo failed']):
            return {
                'category': 'Network Connection Issue',
                'message': 'We couldn\'t establish a stable connection to the server.',
                'suggestion': 'Please check your internet connection and try again. If you\'re using a proxy or firewall, make sure it\'s properly configured in Settings.'
            }
        
        # Server errors
        if any(keyword in error_message for keyword in ['server', '500', '502', '503', '504', 'unavailable', 'service unavailable']):
            return {
                'category': 'Server Temporarily Unavailable',
                'message': 'The platform\'s servers are currently experiencing issues.',
                'suggestion': 'Please try again in a few minutes. This is usually a temporary problem on the platform\'s side, not with our application.'
            }
        
        # Generic fallback
        return {
            'category': 'Unexpected Issue',
            'message': 'Something unexpected happened during the download process.',
            'suggestion': 'Please try again with a different URL or download type. If the problem continues, consider updating the media engine through the Check Updates button.'
        }
    
    @staticmethod
    def format_error_message(original_error, classified_error):
        """Format a detailed error message for the user"""
        return f"{classified_error['category']}\n\n{classified_error['message']}\n\nHow to fix this:\n{classified_error['suggestion']}\n\nTechnical details: {original_error}"


# --- Settings Dialog ---
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QFormLayout()
        
        # Video Quality
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Best", "1080p", "720p", "480p", "360p"])
        layout.addRow("Video Quality:", self.quality_combo)
        
        # Audio Format
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["m4a", "mp3", "wav"])
        layout.addRow("Audio Format:", self.audio_format_combo)
        
        # Max Retries
        self.retries_spinbox = QSpinBox()
        self.retries_spinbox.setRange(0, 10)
        self.retries_spinbox.setValue(5)
        layout.addRow("Max Retries:", self.retries_spinbox)
        
        # Use Proxy
        self.proxy_checkbox = QCheckBox("Use Proxy")
        layout.addRow(self.proxy_checkbox)
        
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("Enter proxy URL (e.g., http://proxy:port)")
        self.proxy_input.setEnabled(False)
        layout.addRow("Proxy URL:", self.proxy_input)
        
        # Connect checkbox to enable/disable proxy input
        self.proxy_checkbox.toggled.connect(self.proxy_input.setEnabled)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addRow(button_layout)
        self.setLayout(layout)


# --- Download History Dialog ---
class DownloadHistoryDialog(QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Download History")
        self.setModal(True)
        self.resize(600, 400)
        self.setWindowFlags(Qt.WindowType.Window)  # Enable standard window controls
        
        # Store the original history for filtering
        self.original_history = history
        self.filtered_history = history
        
        layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Downloads", "Successful Only", "Errors Only"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_history)
        
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(refresh_button)
        layout.addLayout(filter_layout)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Title", "URL", "Date", "Status"])
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setAlternatingRowColors(True)  # Make it easier to read
        
        # Enable sorting
        self.history_table.setSortingEnabled(True)
        header = self.history_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Enable double-click to open file location
        self.history_table.doubleClicked.connect(self.open_file_location)
        
        # Populate history
        self.history = history
        self.populate_history()
        
        layout.addWidget(self.history_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        clear_button = QPushButton("Clear History")
        close_button = QPushButton("Close")
        
        clear_button.clicked.connect(self.clear_history)
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def populate_history(self):
        self.history_table.setRowCount(len(self.filtered_history))
        for row, entry in enumerate(self.filtered_history):
            self.history_table.setItem(row, 0, QTableWidgetItem(entry.get("title", "Unknown")))
            self.history_table.setItem(row, 1, QTableWidgetItem(entry.get("url", "")))
            self.history_table.setItem(row, 2, QTableWidgetItem(entry.get("date", "")))
            self.history_table.setItem(row, 3, QTableWidgetItem(entry.get("status", "")))
    
    def refresh_history(self):
        # Reload history from parent
        parent_window = self.parent()
        if parent_window and isinstance(parent_window, DownloaderApp):
            parent_window.load_download_history()
            self.original_history = parent_window.download_history
            self.apply_filter()  # Reapply current filter
            self.populate_history()
    
    def apply_filter(self):
        filter_text = self.filter_combo.currentText()
        
        if filter_text == "All Downloads":
            self.filtered_history = self.original_history
        elif filter_text == "Successful Only":
            self.filtered_history = [entry for entry in self.original_history 
                                   if not entry.get("status", "").startswith("Error")]
        elif filter_text == "Errors Only":
            self.filtered_history = [entry for entry in self.original_history 
                                   if entry.get("status", "").startswith("Error")]
        
        self.populate_history()
    
    def clear_history(self):
        reply = QMessageBox.question(self, 'Clear History', 
                                   'Are you sure you want to clear all download history?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.history.clear()
            self.history_table.setRowCount(0)
            # Save the cleared history by calling the parent's save method
            parent_window = self.parent()
            if isinstance(parent_window, DownloaderApp):
                parent_window.download_history = self.history
                parent_window.save_download_history()
    def open_file_location(self, index):
        row = index.row()
        if row < len(self.history):
            title = self.history[row].get("title", "Unknown")
            # Set the dialog title to the downloaded file name
            self.setWindowTitle(f"Download History - {title}")
            
            # Get the download path from the parent downloader
            parent_window = self.parent()
            # Check if parent is of the correct type and has downloader attribute
            if parent_window and isinstance(parent_window, DownloaderApp):
                try:
                    download_path = parent_window.downloader.output_path
                    # Open the folder in file explorer
                    self.open_folder(download_path)
                except AttributeError:
                    QMessageBox.warning(self, "Error", "Could not access download folder information.")
    
    def open_folder(self, path):
        try:
            import subprocess
            import platform
            import os
            
            # Check if the path exists
            if not os.path.exists(path):
                QMessageBox.warning(self, "Folder Not Found", 
                                  f"The download folder does not exist:\n{path}")
                return
            
            # Open the folder based on the operating system
            system = platform.system()
            if system == "Windows":
                subprocess.Popen(f'explorer "{os.path.realpath(path)}"')
            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", path])
            else:  # Linux and others
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"Could not open the download folder:\n{str(e)}")

# --- Playlist Selection Dialog ---
class PlaylistSelectionDialog(QDialog):
    def __init__(self, playlist_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Playlist Videos")
        self.setModal(True)
        self.resize(600, 400)
        
        self.playlist_info = playlist_info
        self.selected_videos = []
        
        layout = QVBoxLayout()
        
        # Instructions
        instruction_label = QLabel("Select videos to download from the playlist:")
        instruction_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(instruction_label)
        
        # Playlist info
        playlist_title = playlist_info.get('title', 'Unknown Playlist')
        entries = playlist_info.get('entries', [])
        entries_count = len(entries) if entries else 0
        
        info_label = QLabel(f"Playlist: {playlist_title}\n"
                           f"Total videos: {entries_count}")
        info_label.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Video list
        self.video_list = QTableWidget()
        self.video_list.setColumnCount(3)
        self.video_list.setHorizontalHeaderLabels(["Select", "Title", "Duration"])
        self.video_list.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.video_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Populate video list
        self.populate_video_list()
        
        layout.addWidget(self.video_list)
        
        # Select all/none buttons
        select_layout = QHBoxLayout()
        select_all_button = QPushButton("Select All")
        select_none_button = QPushButton("Select None")
        
        select_all_button.clicked.connect(self.select_all)
        select_none_button.clicked.connect(self.select_none)
        
        select_layout.addWidget(select_all_button)
        select_layout.addWidget(select_none_button)
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Download Selected")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def populate_video_list(self):
        entries = self.playlist_info.get('entries', [])
        self.video_list.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Checkbox for selection
            checkbox = QCheckBox()
            checkbox.setChecked(True)  # Select by default
            self.video_list.setCellWidget(row, 0, checkbox)
            
            # Title
            title = entry.get('title', 'Unknown Title')
            self.video_list.setItem(row, 1, QTableWidgetItem(title))
            
            # Duration
            duration = entry.get('duration', 0)
            if duration > 0:
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            self.video_list.setItem(row, 2, QTableWidgetItem(duration_str))
    
    def select_all(self):
        for row in range(self.video_list.rowCount()):
            checkbox = self.video_list.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(True)
    
    def select_none(self):
        for row in range(self.video_list.rowCount()):
            checkbox = self.video_list.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(False)
    
    def accept(self):
        # Collect selected videos
        self.selected_videos = []
        for row in range(self.video_list.rowCount()):
            checkbox = self.video_list.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                self.selected_videos.append(row)

        
        if not self.selected_videos:
            QMessageBox.warning(self, "No Selection", "Please select at least one video to download.")
            return
            
        super().accept()


# --- Downloader Core Logic ---
class Downloader:
    def __init__(self, output_path="downloads"):
        self.output_path = output_path
        self._progress_hook_callback = None # To set a UI callback for progress
        self._paused = False  # Track pause state
        self._cancelled = False  # Track cancel state
        self.selected_videos = None  # Track selected videos for playlist downloads

    def set_progress_hook(self, callback):
        self._progress_hook_callback = callback

    def _yt_dlp_progress_hook(self, d):
        # Check for pause or cancel requests
        if self._paused:
            d['status'] = 'paused'
        elif self._cancelled:
            d['status'] = 'cancelled'
            raise Exception("Download cancelled by user")
            
        if self._progress_hook_callback:
            self._progress_hook_callback(d)

    def pause(self):
        """Pause the current download"""
        self._paused = True

    def resume(self):
        """Resume the current download"""
        self._paused = False

    def cancel(self):
        """Cancel the current download"""
        self._cancelled = True

    def is_paused(self):
        """Check if download is paused"""
        return self._paused

    def reset_state(self):
        """Reset pause and cancel states"""
        self._paused = False
        self._cancelled = False
        self.selected_videos = None  # Reset selected videos

    def extract_playlist_info(self, url):
        """Extract playlist information without downloading"""
        ydl_opts = {
            'extract_flat': True,  # Don't download, just extract info
            'force_generic_extractor': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return info
            except Exception as e:
                # Log the error for debugging
                print(f"Playlist extraction error: {e}")
                raise Exception(f"Failed to extract playlist info: {e}")

    def download_media(self, url, download_type, settings=None, selected_videos=None):
        print(f"Starting download: type={download_type}, url={url}")
        if selected_videos:
            print(f"Selected videos: {selected_videos}")
        
        os.makedirs(self.output_path, exist_ok=True) # Ensure output directory exists

        # Reset state for new download
        self.reset_state()
        self.selected_videos = selected_videos

        ydl_opts = {
            'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._yt_dlp_progress_hook],
            'ffmpeg_location': self._get_ffmpeg_path(), # Use bundled ffmpeg
            'windowsfilenames': True, # Sanitize filenames for Windows
            'retries': 5, # Retry failed HTTP requests up to 5 times
            'fragment_retries': 5, # Retry fragment downloads
            'socket_timeout': 10, # Set a timeout for socket operations
        }

        # Apply settings if provided
        if settings:
            # Set max retries
            if 'max_retries' in settings:
                ydl_opts['retries'] = settings['max_retries']
                ydl_opts['fragment_retries'] = settings['max_retries']
            
            # Set proxy if enabled
            if settings.get('use_proxy') and settings.get('proxy_url'):
                ydl_opts['proxy'] = settings['proxy_url']

        if download_type == "video":
            # UPDATED: More robust format selection for video
            ydl_opts['format'] = 'bestvideo+bestaudio/best' # Get best video and audio, let yt-dlp/ffmpeg handle
            ydl_opts['merge_output_format'] = 'mp4' # Ensure final output is mp4
            # Explicitly use FFmpeg to convert the video component if needed, ensuring MP4 compatibility
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
            
            # Apply quality settings
            if settings and 'quality' in settings:
                quality = settings['quality']
                if quality != "Best":
                    if quality == "1080p":
                        ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                    elif quality == "720p":
                        ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                    elif quality == "480p":
                        ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
                    elif quality == "360p":
                        ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
        elif download_type == "audio":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '192', # Higher quality
            }]
            ydl_opts['extract_audio'] = True # Ensure audio is extracted
            
            # Apply audio format settings
            if settings and 'audio_format' in settings:
                audio_format = settings['audio_format']
                if audio_format != "m4a":
                    ydl_opts['postprocessors'][0]['preferredcodec'] = audio_format
        elif download_type == "playlist":
            # Handle playlist downloads
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
            
            # For playlists, we want to download all videos by default
            ydl_opts['playliststart'] = 1
            ydl_opts['playlistend'] = None  # Download all videos
            
            # If specific videos are selected, download only those
            if selected_videos and len(selected_videos) > 0:
                # Convert selected video indices to playlist indices (1-based)
                # selected_videos contains 0-based indices from the dialog
                playlist_indices = [str(idx + 1) for idx in selected_videos]
                ydl_opts['playlist_items'] = ','.join(playlist_indices)
                print(f"Playlist items to download: {ydl_opts['playlist_items']}")
            
            # Apply quality settings for playlist
            if settings and 'quality' in settings:
                quality = settings['quality']
                if quality != "Best":
                    if quality == "1080p":
                        ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                    elif quality == "720p":
                        ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                    elif quality == "480p":
                        ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
                    elif quality == "360p":
                        ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
        else:
            raise ValueError("Invalid download type specified.")

        print(f"yt-dlp options: {ydl_opts}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
                return "Download complete!"
            except yt_dlp.utils.DownloadError as e:
                # Classify and format the error
                classified_error = ErrorClassifier.classify_error(str(e))
                formatted_error = ErrorClassifier.format_error_message(str(e), classified_error)
                print(f"Download error: {e}")  # Log for debugging
                return f"Download failed: {formatted_error}"
            except Exception as e:
                # Check if it's a cancellation
                if "cancelled" in str(e).lower():
                    return "Download cancelled by user"
                # Classify and format the error
                classified_error = ErrorClassifier.classify_error(str(e))
                formatted_error = ErrorClassifier.format_error_message(str(e), classified_error)
                print(f"General error: {e}")  # Log for debugging
                return f"Download failed: {formatted_error}"
    
    def _get_ffmpeg_path(self):
        # Determine the base path for locating ffmpeg.exe
        if getattr(sys, 'frozen', False): # Running as bundled exe (PyInstaller)
            # When frozen, sys._MEIPASS is the path to the temporary directory
            # where PyInstaller unpacks all bundled files.
            base_path = os.path.dirname(sys.executable)
            # Use getattr to avoid linter warnings
            _MEIPASS = getattr(sys, '_MEIPASS', None)
            if _MEIPASS:
                base_path = _MEIPASS
        else: # Running as a regular Python script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        ffmpeg_exe_path = os.path.join(base_path, 'ffmpeg.exe')
        
        # DEBUG PRINTS - uncomment these if you need to debug ffmpeg discovery
        # print(f"DEBUG: Application base path: {base_path}")
        # print(f"DEBUG: Checking for ffmpeg at: {ffmpeg_exe_path}")

        if os.path.exists(ffmpeg_exe_path):
            # print(f"DEBUG: FFmpeg found at: {base_path}")
            return base_path # yt-dlp expects the directory containing ffmpeg.exe
        
        # print("DEBUG: FFmpeg not found in bundle/script dir, falling back to system PATH.")
        return None # yt-dlp will try to find it in the system's PATH

# --- Download Manager for Parallel Downloads ---
class DownloadManager:
    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent
        self.active_downloads = []
        self.download_queue = []
        self.completed_downloads = []
        
    def add_download(self, downloader, url, download_type, settings=None, selected_videos=None):
        self.download_queue.append({
            'downloader': downloader,
            'url': url,
            'download_type': download_type,
            'settings': settings,
            'selected_videos': selected_videos
        })
        
    def start_next_download(self):
        if len(self.active_downloads) < self.max_concurrent and self.download_queue:
            download_info = self.download_queue.pop(0)
            
            # Create and start download thread
            thread = DownloadThread(
                download_info['downloader'],
                download_info['url'],
                download_info['download_type'],
                download_info['settings'],
                download_info.get('selected_videos')  # Pass selected videos if available
            )
            
            self.active_downloads.append({
                'thread': thread,
                'info': download_info
            })
            
            # Start the thread
            thread.start()
            
            return thread
        return None
        
    def remove_completed_download(self, thread):
        self.active_downloads = [d for d in self.active_downloads if d['thread'] != thread]
        self.completed_downloads.append(thread)
        
    def has_pending_downloads(self):
        return len(self.download_queue) > 0 or len(self.active_downloads) > 0

# --- Threading for UI Responsiveness ---
class DownloadThread(QThread):
    progress_signal = pyqtSignal(dict) # To send progress updates
    finished_signal = pyqtSignal(str) # To send final status
    error_signal = pyqtSignal(str) # To send error messages

    def __init__(self, downloader, url, download_type, settings=None, selected_videos=None, parent=None):
        super().__init__(parent)
        self.downloader = downloader
        self.url = url
        self.download_type = download_type
        self.settings = settings or {}
        self.selected_videos = selected_videos  # Track selected videos for playlist downloads
        # Set the downloader's hook to emit our signal
        self.downloader.set_progress_hook(self._threaded_progress_hook)
        self._paused = False

    def _threaded_progress_hook(self, d):
        # Handle pause state in the progress hook
        if d.get('status') == 'paused':
            # Wait until resumed
            while self._paused and self.isRunning():
                self.msleep(100)  # Sleep for 100ms and check again
            if not self.isRunning():
                return  # Thread was terminated
        self.progress_signal.emit(d)

    def run(self):
        try:
            result = self.downloader.download_media(self.url, self.download_type, self.settings, self.selected_videos)
            # Check if the result indicates a failure
            if result.startswith("Download failed:"):
                self.error_signal.emit(result)
            elif result == "Download cancelled by user":
                self.error_signal.emit(result)
            else:
                self.finished_signal.emit(result)
        except Exception as e:
            # Classify and format the error
            classified_error = ErrorClassifier.classify_error(str(e))
            formatted_error = ErrorClassifier.format_error_message(str(e), classified_error)
            self.error_signal.emit(f"Download failed: {formatted_error}")

    def pause(self):
        """Pause the download"""
        self._paused = True
        if hasattr(self.downloader, 'pause'):
            self.downloader.pause()

    def resume(self):
        """Resume the download"""
        self._paused = False
        if hasattr(self.downloader, 'resume'):
            self.downloader.resume()

    def cancel(self):
        """Cancel the download"""
        self._paused = False
        if hasattr(self.downloader, 'cancel'):
            self.downloader.cancel()

# --- Notification System ---
class NotificationManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.notifications = []
        self.max_notifications = 50  # Limit stored notifications
        self.load_notification_history()
        
        # Try to initialize system tray icon for desktop notifications
        self.tray_icon = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            try:
                self.tray_icon = QSystemTrayIcon(parent)
                if parent and hasattr(parent, '_get_icon_path'):
                    icon_path = parent._get_icon_path()
                    if icon_path and os.path.exists(icon_path):
                        self.tray_icon.setIcon(QIcon(icon_path))
                self.tray_icon.show()
            except Exception as e:
                print(f"Could not initialize system tray: {e}")
    
    def load_notification_history(self):
        history_file = "notification_history.json"
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            # Use getattr to avoid linter warnings
            _MEIPASS = getattr(sys, '_MEIPASS', None)
            if _MEIPASS:
                base_path = _MEIPASS
            history_path = os.path.join(base_path, history_file)
        else:
            history_path = history_file
            
        if os.path.exists(history_path):
            try:
                with open(history_path, "r") as f:
                    self.notifications = json.load(f)
            except Exception as e:
                print(f"Error loading notification history: {e}")
                self.notifications = []

    def save_notification_history(self):
        history_file = "notification_history.json"
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            # Use getattr to avoid linter warnings
            _MEIPASS = getattr(sys, '_MEIPASS', None)
            if _MEIPASS:
                base_path = _MEIPASS
            history_path = os.path.join(base_path, history_file)
        else:
            history_path = history_file
            
        try:
            with open(history_path, "w") as f:
                # Only save last 100 notifications to prevent file bloat
                recent_notifications = self.notifications[-100:]
                json.dump(recent_notifications, f, indent=2)
        except Exception as e:
            print(f"Error saving notification history: {e}")

    def add_notification(self, title, message, notification_type="info", duration=5000):
        """
        Add a new notification
        notification_type: info, warning, error, success
        duration: milliseconds to show notification (0 for persistent)
        """
        notification = {
            "id": len(self.notifications) + 1,
            "title": title,
            "message": message,
            "type": notification_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "read": False
        }
        
        self.notifications.append(notification)
        
        # Keep only the most recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
        
        # Show desktop notification if available
        self._show_desktop_notification(title, message, notification_type, duration)
        
        # Save notification history
        self.save_notification_history()
        
        return notification

    def _show_desktop_notification(self, title, message, notification_type, duration):
        """Show desktop notification using system tray"""
        if self.tray_icon:
            try:
                # Map notification types to QSystemTrayIcon.MessageIcon
                icon_map = {
                    "info": QSystemTrayIcon.MessageIcon.Information,
                    "warning": QSystemTrayIcon.MessageIcon.Warning,
                    "error": QSystemTrayIcon.MessageIcon.Critical,
                    "success": QSystemTrayIcon.MessageIcon.Information
                }
                
                icon = icon_map.get(notification_type, QSystemTrayIcon.MessageIcon.NoIcon)
                self.tray_icon.showMessage(title, message, icon, duration)
            except Exception as e:
                print(f"Error showing system tray notification: {e}")

    def mark_as_read(self, notification_id):
        """Mark a notification as read"""
        for notification in self.notifications:
            if notification["id"] == notification_id:
                notification["read"] = True
                break
        self.save_notification_history()

    def mark_all_as_read(self):
        """Mark all notifications as read"""
        for notification in self.notifications:
            notification["read"] = True
        self.save_notification_history()

    def get_unread_count(self):
        """Get count of unread notifications"""
        return sum(1 for n in self.notifications if not n["read"])

    def get_notifications(self, limit=None, unread_only=False):
        """Get notifications, optionally filtered"""
        notifications = self.notifications.copy()
        
        if unread_only:
            notifications = [n for n in notifications if not n["read"]]
            
        if limit:
            notifications = notifications[-limit:]  # Get most recent
            
        return notifications[::-1]  # Return in reverse chronological order

    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications.clear()
        self.save_notification_history()

# --- Notification Center Dialog ---
class NotificationCenterDialog(QDialog):
    def __init__(self, notification_manager, parent=None):
        super().__init__(parent)
        self.notification_manager = notification_manager
        self.setWindowTitle("Notification Center")
        self.setModal(False)
        self.resize(500, 400)
        
        self.init_ui()
        self.refresh_notifications()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Notifications")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_all)
        
        mark_read_button = QPushButton("Mark All as Read")
        mark_read_button.clicked.connect(self.mark_all_read)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(mark_read_button)
        header_layout.addWidget(clear_button)
        layout.addLayout(header_layout)
        
        # Notification list
        self.notification_list = QTableWidget()
        self.notification_list.setColumnCount(3)
        self.notification_list.setHorizontalHeaderLabels(["Type", "Message", "Time"])
        self.notification_list.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.notification_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.notification_list.setAlternatingRowColors(True)
        
        header = self.notification_list.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.notification_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def refresh_notifications(self):
        notifications = self.notification_manager.get_notifications()
        self.notification_list.setRowCount(len(notifications))
        
        type_icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }
        
        for row, notification in enumerate(notifications):
            # Type column
            type_item = QTableWidgetItem(type_icons.get(notification["type"], "ℹ️"))
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notification_list.setItem(row, 0, type_item)
            
            # Message column
            message = f"{notification['title']}: {notification['message']}"
            message_item = QTableWidgetItem(message)
            self.notification_list.setItem(row, 1, message_item)
            
            # Time column
            timestamp = datetime.datetime.fromisoformat(notification["timestamp"])
            time_str = timestamp.strftime("%Y-%m-%d %H:%M")
            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notification_list.setItem(row, 2, time_item)
            
            # Mark as read when viewed
            if not notification["read"]:
                self.notification_manager.mark_as_read(notification["id"])

    def clear_all(self):
        self.notification_manager.clear_notifications()
        self.refresh_notifications()

    def mark_all_read(self):
        self.notification_manager.mark_all_as_read()
        self.refresh_notifications()

# --- PyQt6 GUI Application ---
class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.downloader = Downloader() # Initialize downloader with default path
        self.download_thread = None
        self.settings = {}  # Store user settings
        self.download_history = []  # Store download history
        self.download_queue = []  # Queue for batch downloads
        self.current_download_index = 0  # Track current download in queue
        self.total_downloads = 0  # Track total number of downloads in batch
        self.download_manager = DownloadManager(max_concurrent=3)  # Parallel download manager
        self.last_update_check = None  # Track when we last checked for updates
        self.is_downloading = False  # Track download state
        self.last_downloaded_filename = None  # Track the last downloaded filename
        
        # Initialize notification system
        self.notification_manager = NotificationManager(self)
        
        self.initUI()
        self.load_settings() # Load last saved directory
        self.load_app_settings() # Load app settings
        self.load_download_history() # Load download history
        self.check_for_updates() # Check for updates on startup
        
        # Show startup notification
        self.notification_manager.add_notification(
            "Application Started", 
            "Media Downloader is ready to use", 
            "success"
        )

    def initUI(self):
        self.setWindowTitle("Media Downloader")
        self.setGeometry(100, 100, 600, 400) # Increased height for text area
        self.setWindowIcon(QIcon(self._get_icon_path())) # Set application icon
        
        # Create settings button instead of menu
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings)
        
        # Create history button
        history_button = QPushButton("History")
        history_button.clicked.connect(self.open_history)
        
        # Create update button
        update_button = QPushButton("Check Updates")
        update_button.clicked.connect(self.manual_update_check)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Add settings, history, and update buttons to top
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(settings_button)
        top_layout.addWidget(history_button)
        top_layout.addWidget(update_button)
        main_layout.addLayout(top_layout)

        # URL Input - Changed to QTextEdit for multi-line input
        url_layout = QHBoxLayout()
        self.url_input = QTextEdit(self)
        self.url_input.setPlaceholderText("Paste your media links here (one per line)\nWorks with YouTube, Facebook, Instagram, TikTok, Twitter, Vimeo, and many other platforms")
        self.url_input.setMaximumHeight(100)
        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout)

        # Download Buttons
        button_layout = QHBoxLayout()
        self.video_button = QPushButton("Download Video", self)
        self.video_button.clicked.connect(lambda: self.start_download("video"))
        self.video_button.setFixedHeight(40)
        self.video_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(self.video_button)

        self.audio_button = QPushButton("Download Audio", self)
        self.audio_button.clicked.connect(lambda: self.start_download("audio"))
        self.audio_button.setFixedHeight(40)
        self.audio_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        button_layout.addWidget(self.audio_button)
        
        self.playlist_button = QPushButton("Download Playlist", self)
        self.playlist_button.clicked.connect(lambda: self.start_download("playlist"))
        self.playlist_button.setFixedHeight(40)
        self.playlist_button.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        button_layout.addWidget(self.playlist_button)
        main_layout.addLayout(button_layout)

        # Output Directory Selector
        output_layout = QHBoxLayout()
        self.output_dir_label = QLabel(f"Save to: {self.downloader.output_path}", self)
        self.output_dir_label.setStyleSheet("font-style: italic; color: #555;")
        output_layout.addWidget(self.output_dir_label)

        self.output_dir_button = QPushButton("Change Folder", self)
        self.output_dir_button.clicked.connect(self.select_output_directory)
        self.output_dir_button.setFixedWidth(120)
        output_layout.addWidget(self.output_dir_button)
        main_layout.addLayout(output_layout)

        # Progress Bar and Controls
        progress_layout = QVBoxLayout()
        
        # Progress Bar - Initially hidden
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)  # Hide initially
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #007BFF;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Download Controls
        self.controls_layout = QHBoxLayout()
        self.pause_button = QPushButton("Pause")
        self.retry_button = QPushButton("Retry")
        self.cancel_button = QPushButton("Cancel")
        
        self.pause_button.clicked.connect(self.pause_download)
        self.retry_button.clicked.connect(self.retry_download)
        self.cancel_button.clicked.connect(self.cancel_download)
        
        self.pause_button.setEnabled(False)
        self.retry_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        
        self.controls_layout.addWidget(self.pause_button)
        self.controls_layout.addWidget(self.retry_button)
        self.controls_layout.addWidget(self.cancel_button)
        self.controls_layout.addStretch()
        
        progress_layout.addLayout(self.controls_layout)
        main_layout.addLayout(progress_layout)

        # Status Label - Updated with more user-friendly message
        self.status_label = QLabel("Ready to download your media files.", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #333;")
        main_layout.addWidget(self.status_label)
        
        # Add a stretch to push content to top
        main_layout.addStretch()

        self.setLayout(main_layout)

    def _get_icon_path(self):
        # Look for icon.ico in the same directory as the script or bundled location
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            # Use getattr to avoid linter warnings
            _MEIPASS = getattr(sys, '_MEIPASS', None)
            if _MEIPASS:
                base_path = _MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        icon_path = os.path.join(base_path, 'icon.ico')
        if os.path.exists(icon_path):
            return icon_path
        return "" # No icon found

    def load_settings(self):
        # Simple persistence: Load last used directory from a file
        settings_file = "app_settings.txt"
        # Adjust path for bundled app
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            # Use getattr to avoid linter warnings
            _MEIPASS = getattr(sys, '_MEIPASS', None)
            if _MEIPASS:
                base_path = _MEIPASS
            settings_path = os.path.join(base_path, settings_file)
        else:
            settings_path = settings_file

        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as f:
                    last_dir = f.readline().strip()
                    if os.path.isdir(last_dir): # Validate directory exists
                        self.downloader.output_path = last_dir
                        self.output_dir_label.setText(f"Output: {self.downloader.output_path}")
            except Exception as e:
                print(f"Error loading settings: {e}")
                # Fallback to default path if settings file is corrupted or unreadable
                self.downloader.output_path = "downloads"
                self.output_dir_label.setText(f"Output: {self.downloader.output_path}")

    def save_settings(self):
        # Simple persistence: Save current directory to a file
        settings_file = "app_settings.txt"
        # Adjust path for bundled app
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            # Use getattr to avoid linter warnings
            _MEIPASS = getattr(sys, '_MEIPASS', None)
            if _MEIPASS:
                base_path = _MEIPASS
            settings_path = os.path.join(base_path, settings_file)
        else:
            settings_path = settings_file
            
        try:
            with open(settings_path, "w") as f:
                f.write(self.downloader.output_path)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def open_settings(self):
        dialog = SettingsDialog(self)
        # Pre-populate dialog with current settings
        if 'quality' in self.settings:
            index = dialog.quality_combo.findText(self.settings['quality'])
            if index >= 0:
                dialog.quality_combo.setCurrentIndex(index)
        
        if 'audio_format' in self.settings:
            index = dialog.audio_format_combo.findText(self.settings['audio_format'])
            if index >= 0:
                dialog.audio_format_combo.setCurrentIndex(index)
                
        if 'max_retries' in self.settings:
            dialog.retries_spinbox.setValue(self.settings['max_retries'])
            
        if 'use_proxy' in self.settings:
            dialog.proxy_checkbox.setChecked(self.settings['use_proxy'])
            
        if 'proxy_url' in self.settings:
            dialog.proxy_input.setText(self.settings['proxy_url'])
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Save settings
            self.settings['quality'] = dialog.quality_combo.currentText()
            self.settings['audio_format'] = dialog.audio_format_combo.currentText()
            self.settings['max_retries'] = dialog.retries_spinbox.value()
            self.settings['use_proxy'] = dialog.proxy_checkbox.isChecked()
            self.settings['proxy_url'] = dialog.proxy_input.text()
            self.save_app_settings()

    def load_app_settings(self):
        settings_file = "app_config.json"
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            # Use getattr to avoid linter warnings
            _MEIPASS = getattr(sys, '_MEIPASS', None)
            if _MEIPASS:
                base_path = _MEIPASS
            settings_path = os.path.join(base_path, settings_file)
        else:
            settings_path = settings_file
            
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as f:
                    import json
                    self.settings = json.load(f)
            except Exception as e:
                print(f"Error loading app settings: {e}")
                self.settings = {}

    def save_app_settings(self):
        settings_file = "app_config.json"
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            # Use getattr to avoid linter warnings
            _MEIPASS = getattr(sys, '_MEIPASS', None)
            if _MEIPASS:
                base_path = _MEIPASS
            settings_path = os.path.join(base_path, settings_file)
        else:
            settings_path = settings_file
            
        try:
            with open(settings_path, "w") as f:
                import json
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving app settings: {e}")

    def open_history(self):
        dialog = DownloadHistoryDialog(self.download_history, self)
        dialog.exec()

    def load_download_history(self):
        history_file = "download_history.json"
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            # Use getattr to avoid linter warnings
            _MEIPASS = getattr(sys, '_MEIPASS', None)
            if _MEIPASS:
                base_path = _MEIPASS
            history_path = os.path.join(base_path, history_file)
        else:
            history_path = history_file
            
        if os.path.exists(history_path):
            try:
                with open(history_path, "r") as f:
                    self.download_history = json.load(f)
            except Exception as e:
                print(f"Error loading download history: {e}")
                self.download_history = []


    def save_download_history(self):
        history_file = "download_history.json"
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
            # Use getattr to avoid linter warnings
            _MEIPASS = getattr(sys, '_MEIPASS', None)
            if _MEIPASS:
                base_path = _MEIPASS
            history_path = os.path.join(base_path, history_file)
        else:
            history_path = history_file
            
        try:
            with open(history_path, "w") as f:
                json.dump(self.download_history, f, indent=2)
        except Exception as e:
            print(f"Error saving download history: {e}")

    def add_to_history(self, title, url, status):
        entry = {
            "title": title,
            "url": url,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status
        }
        self.download_history.append(entry)
        self.save_download_history()

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if directory:
            self.downloader.output_path = directory
            self.output_dir_label.setText(f"Output: {directory}")
            self.status_label.setText(f"Download folder set to: {directory}")
            self.save_settings() # Save the new directory

    def start_download(self, download_type):
        # Get all URLs from the text area
        urls_text = self.url_input.toPlainText().strip()
        if not urls_text:
            QMessageBox.warning(self, "Input Error", "Please enter at least one URL to download.")
            return
            
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # For single URL with playlist type, show playlist selection
        if len(urls) == 1 and download_type == "playlist":
            self.process_playlist_url(urls[0])
        elif len(urls) == 1:
            # For single non-playlist URL, use existing logic
            self.process_single_url(urls[0], download_type)
        else:
            # For multiple URLs, use batch download
            self.process_batch_urls(urls, download_type)

    def process_playlist_url(self, url):
        """Handle playlist URL with selection dialog"""
        try:
            self.status_label.setText("Extracting playlist information...")
            QApplication.processEvents()  # Update UI to show the message
            
            playlist_info = self.downloader.extract_playlist_info(url)
            if playlist_info is None:
                raise Exception("Failed to extract playlist information")
            
            # Check if playlist has entries
            entries = playlist_info.get('entries', [])
            if not entries:
                QMessageBox.information(self, "Empty Playlist", 
                                      "The playlist appears to be empty or private.\n\n"
                                      "Please check if the playlist URL is correct and public.")
                self.status_label.setText("Playlist is empty or inaccessible.")
                return
            
            dialog = PlaylistSelectionDialog(playlist_info, self)
            self.status_label.setText("Ready to download your media files.")
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Use the selected videos from the dialog
                selected_videos = dialog.selected_videos
                if selected_videos:
                    count = len(selected_videos)
                    self.status_label.setText(f"Starting download of {count} selected videos...")
                    # Create and start the download thread with settings and selected videos
                    self.start_download_thread(url, "playlist", selected_videos)
                else:
                    self.status_label.setText("No videos selected for download.")
            else:
                # User cancelled the dialog
                self.status_label.setText("Playlist download cancelled by user.")
        except Exception as e:
            error_msg = str(e)
            print(f"Playlist processing error: {error_msg}")  # Log for debugging
            self.status_label.setText("Failed to process playlist.")
            QMessageBox.warning(self, "Playlist Processing Error", 
                              f"Could not process the playlist:\n\n{error_msg}\n\n"
                              "Please check the URL and try again. If the problem persists, "
                              "the playlist might be private or unavailable.")

    def process_single_url(self, url, download_type):
        # Auto-detect playlist URLs
        if download_type == "video" or download_type == "audio":
            # Check if it's actually a playlist URL
            playlist_indicators = ['playlist', 'list=', 'channel', 'user/']
            if any(indicator in url.lower() for indicator in playlist_indicators):
                reply = QMessageBox.question(self, 'Playlist Detected', 
                                           'This URL appears to be a playlist.\n\n'
                                           'Do you want to:\n'
                                           '• YES: Select specific videos from the playlist\n'
                                           '• NO: Download the entire playlist\n'
                                           '• Cancel: Cancel this operation',
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                                           QMessageBox.StandardButton.Yes)
                
                if reply == QMessageBox.StandardButton.Cancel:
                    self.status_label.setText("Operation cancelled by user.")
                    return
                elif reply == QMessageBox.StandardButton.Yes:
                    download_type = "playlist"
                    
                    # Extract playlist info and show selection dialog
                    try:
                        self.status_label.setText("Extracting playlist information...")
                        QApplication.processEvents()  # Update UI to show the message
                        
                        playlist_info = self.downloader.extract_playlist_info(url)
                        if playlist_info is None:
                            raise Exception("Failed to extract playlist information")
                        
                        # Check if playlist has entries
                        entries = playlist_info.get('entries', [])
                        if not entries:
                            QMessageBox.information(self, "Empty Playlist", 
                                                  "The playlist appears to be empty or private.\n\n"
                                                  "Please check if the playlist URL is correct and public.")
                            self.status_label.setText("Playlist is empty or inaccessible.")
                            return
                        
                        dialog = PlaylistSelectionDialog(playlist_info, self)
                        self.status_label.setText("Ready to download your media files.")
                        
                        if dialog.exec() == QDialog.DialogCode.Accepted:
                            # Use the selected videos from the dialog
                            selected_videos = dialog.selected_videos
                            if selected_videos:
                                count = len(selected_videos)
                                self.status_label.setText(f"Starting download of {count} selected videos...")
                                # Create and start the download thread with settings and selected videos
                                self.start_download_thread(url, download_type, selected_videos)
                                return  # Exit early since we've started the download
                            else:
                                self.status_label.setText("No videos selected for download.")
                                return
                        else:
                            # User cancelled the dialog
                            self.status_label.setText("Playlist download cancelled by user.")
                            return
                    except Exception as e:
                        error_msg = str(e)
                        print(f"Playlist processing error: {error_msg}")  # Log for debugging
                        self.status_label.setText("Failed to process playlist.")
                        QMessageBox.warning(self, "Playlist Processing Error", 
                                          f"Could not process the playlist:\n\n{error_msg}\n\n"
                                          "Downloading as a regular video instead.")
                # If user clicked "No", we continue with download_type="playlist" to download the entire playlist

        # For non-playlist downloads or if user chose to download entire playlist
        self.start_download_thread(url, download_type)

    def start_download_thread(self, url, download_type, selected_videos=None):
        # Disable buttons during download
        self.video_button.setEnabled(False)
        self.audio_button.setEnabled(False)
        self.playlist_button.setEnabled(False)
        self.output_dir_button.setEnabled(False)
        self.url_input.setEnabled(False)
        
        # Enable control buttons
        self.pause_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.retry_button.setEnabled(False)

        # Show progress bar when starting download
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)  # Set to 0% only when starting a download
        self.status_label.setText(f"Starting {download_type} download...")
        self.is_downloading = True

        # Create and start the download thread with settings
        self.download_thread = DownloadThread(self.downloader, url, download_type, self.settings, selected_videos)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.error_signal.connect(self.download_error)
        self.download_thread.start()

    def process_batch_urls(self, urls, download_type):
        # For batch downloads, create a queue
        # Note: For simplicity, we're not handling playlist selection in batch mode
        # In batch mode, playlists will be downloaded entirely
        self.download_queue = [(url, download_type) for url in urls]  # (url, download_type)
        self.current_download_index = 0
        self.total_downloads = len(urls)
        
        # Disable buttons during batch download
        self.video_button.setEnabled(False)
        self.audio_button.setEnabled(False)
        self.playlist_button.setEnabled(False)
        self.output_dir_button.setEnabled(False)
        self.url_input.setEnabled(False)
        
        # Show progress bar when starting batch download
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Starting batch download: {len(urls)} items in queue")
        
        # Add all downloads to the download manager
        for url, d_type in self.download_queue:
            # For batch downloads, we don't handle playlist selection
            self.download_manager.add_download(self.downloader, url, d_type, self.settings, None)
        
        # Start parallel downloads
        self.start_parallel_downloads()

    def download_finished(self, message):
        self.status_label.setText("Download completed successfully!")
        self.progress_bar.setValue(100)
        self._reset_ui_state()
        self.is_downloading = False
        
        # Add to history
        url = self.url_input.toPlainText().strip().split('\n')[0] if self.url_input.toPlainText().strip() else ""
        
        # Use the actual downloaded filename if available
        if self.last_downloaded_filename:
            title = self.last_downloaded_filename
            # Remove file extension for cleaner display
            if '.' in title:
                title = '.'.join(title.split('.')[:-1])
        else:
            title = "Unknown Title"
            # Try to extract title from message or use a default
            if "complete" in message.lower():
                title = message.replace("Download complete!", "").strip() or "Downloaded Media"
        
        self.add_to_history(title, url, "Success")
        
        # Add notification
        self.notification_manager.add_notification(
            "Download Complete", 
            f"File '{title}' downloaded successfully", 
            "success"
        )
        
        QMessageBox.information(self, "Download Complete", 
                              f"Great job! Your file has been successfully downloaded.\n\n"
                              f"File: {title}\n"
                              f"Location: {self.downloader.output_path}\n\n"
                              "Enjoy your media!")

    def download_error(self, message):
        self.status_label.setText("Download encountered an issue")
        self._reset_ui_state()
        self.is_downloading = False
        
        # Add to history
        url = self.url_input.toPlainText().strip().split('\n')[0] if self.url_input.toPlainText().strip() else ""
        
        # Classify and format the error for better user experience
        classified_error = ErrorClassifier.classify_error(message)
        formatted_error = ErrorClassifier.format_error_message(message, classified_error)
        
        self.add_to_history("Unknown Title", url, "Error: " + classified_error['category'])
        
        # Add notification
        self.notification_manager.add_notification(
            "Download Failed", 
            f"Download failed: {classified_error['category']}", 
            "error"
        )
        
        QMessageBox.critical(self, f"Download Issue - {classified_error['category']}", formatted_error)

    def update_progress(self, d):
        if d['status'] == 'downloading':
            try:
                # yt-dlp's _percent_str can be tricky, sometimes it's like ' 50.1%'
                percent_str = d.get('_percent_str', '0%').strip().replace('%', '')
                percent = float(percent_str)
                self.progress_bar.setValue(int(percent))
                # Display file name if available
                filename = d.get('filename', 'Unknown File')
                if isinstance(filename, list): # sometimes filename can be a list of paths
                    filename = os.path.basename(filename[0])
                else:
                    filename = os.path.basename(filename)

                # Trim filename for display if too long
                display_filename = filename
                if len(display_filename) > 50:
                    display_filename = display_filename[:25] + "..." + display_filename[-25:]

                self.status_label.setText(
                    f"Downloading: {display_filename} - {d['_percent_str']} ({d.get('_speed_str', 'N/A')}) - ETA: {d.get('_eta_str', 'N/A')}"
                )
            except ValueError:
                # Handle cases where percent_str might not be a valid float
                self.status_label.setText(f"Downloading: {d.get('status')} - {d.get('_percent_str', '')}")
            except Exception as e:
                self.status_label.setText(f"Progress update error: {e}")
        elif d['status'] == 'finished':
            self.progress_bar.setValue(100)
            self.status_label.setText("Processing final file...")
            # Capture the filename when download is finished
            filename = d.get('filename', 'Unknown File')
            if isinstance(filename, list): # sometimes filename can be a list of paths
                filename = os.path.basename(filename[0])
            else:
                filename = os.path.basename(filename)
            # Store the filename for use in download_finished
            self.last_downloaded_filename = filename
        elif d['status'] == 'error':
            # Classify and format the error for better user experience
            error_msg = d.get('error', 'Unknown error')
            classified_error = ErrorClassifier.classify_error(error_msg)
            formatted_error = ErrorClassifier.format_error_message(error_msg, classified_error)
            self.status_label.setText(f"Download error: {classified_error['category']} - {classified_error['message']}")
            
            # Show automatic feedback for connection problems
            if 'network' in classified_error['category'].lower() or 'connection' in classified_error['category'].lower():
                QMessageBox.warning(self, "Connection Issue", 
                                  f"We detected a connection problem during your download:\n\n"
                                  f"{classified_error['message']}\n\n"
                                  f"How to fix this:\n{classified_error['suggestion']}\n\n"
                                  "Please check your internet connection and try again.")
    
    def _reset_ui_state(self):
        self.video_button.setEnabled(True)
        self.audio_button.setEnabled(True)
        self.playlist_button.setEnabled(True)
        self.output_dir_button.setEnabled(True)
        self.url_input.setEnabled(True)
        self.download_thread = None # Clear reference to the finished thread
        self.download_queue = []  # Clear the queue
        self.current_download_index = 0  # Reset index
        self.is_downloading = False
        
        # Reset control buttons
        self.pause_button.setEnabled(False)
        self.retry_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        
        # Hide progress bar when download is complete
        self.progress_bar.setVisible(False)

    def pause_download(self):
        """Pause the current download"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.pause()
            self.pause_button.setEnabled(False)
            self.retry_button.setEnabled(True)
            self.status_label.setText("Download paused. Click Retry to continue.")

    def retry_download(self):
        """Resume the current download"""
        if self.download_thread:
            self.download_thread.resume()
            self.pause_button.setEnabled(True)
            self.retry_button.setEnabled(False)
            self.status_label.setText("Resuming download...")

    def cancel_download(self):
        """Cancel the current download"""
        if self.download_thread and self.download_thread.isRunning():
            reply = QMessageBox.question(self, 'Cancel Download', 
                                       'Are you sure you want to cancel this download?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.download_thread.cancel()
                self._reset_ui_state()
                self.progress_bar.setValue(0)
                self.status_label.setText("Download cancelled by user.")

    def start_parallel_downloads(self):
        # Start as many downloads as allowed by the concurrency limit
        started_threads = []
        while len(started_threads) < self.download_manager.max_concurrent:
            thread = self.download_manager.start_next_download()
            if thread:
                thread.progress_signal.connect(self.update_progress)
                thread.finished_signal.connect(self.parallel_download_finished)
                thread.error_signal.connect(self.parallel_download_error)
                started_threads.append(thread)
            else:
                break
                
        # Update status to show which downloads are in progress
        if started_threads:
            in_progress_count = len(started_threads)
            if self.current_download_index < self.total_downloads:
                self.status_label.setText(f"Downloading {in_progress_count} item(s)... Completed {self.current_download_index}/{self.total_downloads}")
                
        if not started_threads and not self.download_manager.has_pending_downloads():
            # All downloads completed
            self.status_label.setText("All downloads completed successfully!")
            self.progress_bar.setValue(100)
            self._reset_ui_state()
            QMessageBox.information(self, "Batch Download Complete", 
                                  f"Excellent! All {len(self.download_queue)} files have been downloaded successfully.\n\n"
                                  f"Files are saved in: {self.downloader.output_path}\n\n"
                                  "Enjoy your media collection!")

    def parallel_download_finished(self, message):
        # Update progress for completed download
        completed = self.current_download_index + 1
        progress_percent = int((completed / self.total_downloads) * 100)
        self.progress_bar.setValue(progress_percent)
        
        # Add to history
        if self.current_download_index < len(self.download_queue):
            url, _ = self.download_queue[self.current_download_index]
            
            # Try to extract filename from message
            title = "Unknown Title"
            if "complete" in message.lower():
                title = message.replace("Download complete!", "").strip() or f"Batch Item {self.current_download_index + 1}"
                # Remove file extension for cleaner display
                if '.' in title:
                    title = '.'.join(title.split('.')[:-1])
            
            self.add_to_history(title, url, "Success")
        
        # Add notification for batch downloads
        if self.current_download_index == self.total_downloads:
            self.notification_manager.add_notification(
                "Batch Download Complete", 
                f"All {len(self.download_queue)} files downloaded successfully", 
                "success"
            )
        
        # Move to next download
        self.current_download_index += 1
        
        # Update status label to show progress
        if self.current_download_index < self.total_downloads:
            self.status_label.setText(f"Completed {completed}/{self.total_downloads} downloads")
        
        # Start next download if available
        self.start_parallel_downloads()

    def parallel_download_error(self, message):
        # Update progress for completed download (even if it failed)
        completed = self.current_download_index + 1
        progress_percent = int((completed / self.total_downloads) * 100)
        self.progress_bar.setValue(progress_percent)
        
        # Initialize error variables
        classified_error = None
        formatted_error = None
        
        # Add to history
        if self.current_download_index < len(self.download_queue):
            url, _ = self.download_queue[self.current_download_index]
            
            # Classify and format the error for better user experience
            classified_error = ErrorClassifier.classify_error(message)
            formatted_error = ErrorClassifier.format_error_message(message, classified_error)
            
            # Use a generic title for batch items
            title = f"Batch Item {self.current_download_index + 1}"
            self.add_to_history(title, url, "Error: " + classified_error['category'])
            
            # Show error message for the first error in batch
            if self.current_download_index == 0:
                QMessageBox.critical(self, f"Download Issue - {classified_error['category']}", formatted_error)
        
        # Add notification for batch download errors
        if classified_error is not None:
            self.notification_manager.add_notification(
                "Batch Download Error", 
                f"Error downloading item {self.current_download_index + 1}: {classified_error['category']}", 
                "error"
            )
        else:
            self.notification_manager.add_notification(
                "Batch Download Error", 
                f"Error downloading item {self.current_download_index + 1}", 
                "error"
            )
        
        # Move to next download
        self.current_download_index += 1
        
        # Update status label to show progress
        if self.current_download_index < self.total_downloads:
            self.status_label.setText(f"Completed {completed}/{self.total_downloads} downloads")
        
        # Start next download if available
        self.start_parallel_downloads()

    def check_for_updates(self):
        """Check for updates automatically (called on startup) - Now realtime"""
        # Import time here to avoid import issues
        import time
        
        # Note: Removed the 24-hour cooldown to make it realtime as requested
        # Previously: if self.last_update_check and time.time() - self.last_update_check < 24 * 60 * 60: return
        
        # Perform update checks in a separate thread to avoid blocking UI
        self.last_update_check = time.time()
        
        # Check for media engine updates
        try:
            update_info = UpdateChecker.check_yt_dlp_update()
            if update_info['status'] == 'update_available':
                reply = QMessageBox.question(
                    self, 
                    'Update Available', 
                    f'A new version of the media engine is available!\n\n'
                    f'Current: {update_info["current_version"]}\n'
                    f'Latest: {update_info["latest_version"]}\n\n'
                    f'Would you like to update now?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.update_yt_dlp()
                # Add notification
                self.notification_manager.add_notification(
                    "Update Available", 
                    f"New media engine version available: {update_info['latest_version']}", 
                    "info"
                )
        except Exception as e:
            print(f"Error checking for media engine updates: {e}")
        
        # Check for app updates (optional)
        # You can uncomment this if you want to check for app updates
        # try:
        #     app_update = UpdateChecker.check_app_update()
        #     if app_update['status'] == 'update_available':
        #         dialog = UpdateDialog(app_update, self)
        #         if dialog.exec() == QDialog.DialogCode.Accepted:
        #             # Handle app update (open download URL in browser)
        #             import webbrowser
        #             webbrowser.open(app_update['download_url'])
        # except Exception as e:
        #     print(f"Error checking for app updates: {e}")

    def manual_update_check(self):
        """Manually check for updates (called when user clicks update button)"""
        self.status_label.setText("Checking for updates - please wait...")
        
        try:
            # Check for media engine updates
            update_info = UpdateChecker.check_yt_dlp_update()
            
            if update_info['status'] == 'error':
                QMessageBox.warning(self, "Update Check Failed", update_info['message'])
                # Add notification
                self.notification_manager.add_notification(
                    "Update Check Failed", 
                    "Failed to check for updates", 
                    "error"
                )
            elif update_info['status'] == 'update_available':
                reply = QMessageBox.question(
                    self, 
                    'Update Available', 
                    f'Good news! A newer version of the media engine is available.\n\n'
                    f'Your version: {update_info["current_version"]}\n'
                    f'Latest version: {update_info["latest_version"]}\n\n'
                    f'Release Notes:\n{update_info.get("release_notes", "No release notes available")[:300]}...\n\n'
                    f'Would you like to update now for the latest features and improvements?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.update_yt_dlp()
                else:
                    self.status_label.setText("Update check completed - update available but skipped.")
                    # Add notification
                    self.notification_manager.add_notification(
                        "Update Available", 
                        f"Media engine update {update_info['latest_version']} available", 
                        "info"
                    )
            else:
                QMessageBox.information(self, "Up to Date", 
                                      f"Great! Your media engine version ({update_info['current_version']}) is already up to date.\n\n"
                                      "You're enjoying the latest features and improvements.")
                self.status_label.setText("Media engine is up to date.")
                # Add notification
                self.notification_manager.add_notification(
                    "Up to Date", 
                    "Media engine is up to date", 
                    "success"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Update Check Failed", 
                               f"We encountered an unexpected issue while checking for updates:\n\n"
                               f"• {str(e)}\n\n"
                               "Please try again later or check your network connection.")
            self.status_label.setText("Update check failed.")
            # Add notification
            self.notification_manager.add_notification(
                "Update Check Failed", 
                "Failed to check for updates", 
                "error"
            )

    def update_yt_dlp(self):
        """Update the media engine"""
        self.status_label.setText("Updating media engine - please wait...")
        
        try:
            result = UpdateChecker.update_yt_dlp()
            if result['status'] == 'success':
                QMessageBox.information(self, "Update Successful", result['message'])
                self.status_label.setText("Media engine updated successfully!")
                # Add notification
                self.notification_manager.add_notification(
                    "Update Successful", 
                    "Media engine updated successfully", 
                    "success"
                )
            else:
                QMessageBox.critical(self, "Update Failed", result['message'])
                self.status_label.setText("Media engine update failed.")
                # Add notification
                self.notification_manager.add_notification(
                    "Update Failed", 
                    "Failed to update media engine", 
                    "error"
                )
        except Exception as e:
            QMessageBox.critical(self, "Update Failed", 
                               f"We encountered an unexpected issue while updating the media engine:\n\n"
                               f"• {str(e)}\n\n"
                               "Please try again or manually update using pip.")
            self.status_label.setText("Media engine update failed.")
            # Add notification
            self.notification_manager.add_notification(
                "Update Failed", 
                "Failed to update media engine", 
                "error"
            )

if __name__ == '__main__':
    # Ensure sys.argv is correctly handled for PyInstaller bundles
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the search path to include the PyInstaller temporary
        # directory and the `ffmpeg` directory.
        # This makes sure os.path.abspath(__file__) returns the path to
        # the exe itself, not a temporary script in the bundle.
        application_path = os.path.dirname(sys.executable)
        # Use getattr to avoid linter warnings
        _MEIPASS = getattr(sys, '_MEIPASS', None)
        if _MEIPASS:
            application_path = _MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Optional: Set the current working directory to the application path
    # This helps when looking for ffmpeg.exe or icon.ico
    os.chdir(application_path)

    # Create application
    app = QApplication(sys.argv)
    
    # Set application icon for Windows title bar
    icon_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Check for existing instance
    socket = QLocalSocket()
    socket.connectToServer("MediaDownloader_Instance_Check")
    
    if socket.waitForConnected(1000):
        # Another instance is already running
        print("Another instance of Media Downloader is already running.")
        sys.exit(0)
    
    # Create server to prevent future instances
    server = QLocalServer()
    server.listen("MediaDownloader_Instance_Check")
    
    # Create and show main window
    ex = DownloaderApp()
    ex.show()
    
    # Try setting the window icon again after showing the window
    icon_path = ex._get_icon_path()
    if icon_path and os.path.exists(icon_path):
        ex.setWindowIcon(QIcon(icon_path))
    
    # Start application
    exit_code = app.exec()
    
    # Clean up server
    server.close()
    sys.exit(exit_code)