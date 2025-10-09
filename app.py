import sys
import os
import yt_dlp
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QProgressBar, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon # For application icon

# --- Downloader Core Logic ---
class Downloader:
    def __init__(self, output_path="downloads"):
        self.output_path = output_path
        self._progress_hook_callback = None # To set a UI callback for progress

    def set_progress_hook(self, callback):
        self._progress_hook_callback = callback

    def _yt_dlp_progress_hook(self, d):
        if self._progress_hook_callback:
            self._progress_hook_callback(d)

    def download_media(self, url, download_type):
        os.makedirs(self.output_path, exist_ok=True) # Ensure output directory exists

        ydl_opts = {
            'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._yt_dlp_progress_hook],
            'ffmpeg_location': self._get_ffmpeg_path(), # Use bundled ffmpeg
            'windowsfilenames': True, # Sanitize filenames for Windows
            'retries': 5, # Retry failed HTTP requests up to 5 times
            'fragment_retries': 5, # Retry fragment downloads
            'socket_timeout': 10, # Set a timeout for socket operations
        }

        if download_type == "video":
            # UPDATED: More robust format selection for video
            ydl_opts['format'] = 'bestvideo+bestaudio/best' # Get best video and audio, let yt-dlp/ffmpeg handle
            ydl_opts['merge_output_format'] = 'mp4' # Ensure final output is mp4
            # Explicitly use FFmpeg to convert the video component if needed, ensuring MP4 compatibility
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        elif download_type == "audio":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '192', # Higher quality
            }]
            ydl_opts['extract_audio'] = True # Ensure audio is extracted
        else:
            raise ValueError("Invalid download type specified.")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
                return "Download complete!"
            except yt_dlp.utils.DownloadError as e:
                # Catch specific yt-dlp download errors
                return f"Download failed: {e}"
            except Exception as e:
                return f"An unexpected error occurred: {e}"
    
    def _get_ffmpeg_path(self):
        # Determine the base path for locating ffmpeg.exe
        if getattr(sys, 'frozen', False): # Running as bundled exe (PyInstaller)
            # When frozen, sys._MEIPASS is the path to the temporary directory
            # where PyInstaller unpacks all bundled files.
            base_path = sys._MEIPASS
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

# --- Threading for UI Responsiveness ---
class DownloadThread(QThread):
    progress_signal = pyqtSignal(dict) # To send progress updates
    finished_signal = pyqtSignal(str) # To send final status
    error_signal = pyqtSignal(str) # To send error messages

    def __init__(self, downloader, url, download_type, parent=None):
        super().__init__(parent)
        self.downloader = downloader
        self.url = url
        self.download_type = download_type
        # Set the downloader's hook to emit our signal
        self.downloader.set_progress_hook(self._threaded_progress_hook)

    def _threaded_progress_hook(self, d):
        self.progress_signal.emit(d)

    def run(self):
        try:
            result = self.downloader.download_media(self.url, self.download_type)
            self.finished_signal.emit(result)
        except Exception as e:
            self.error_signal.emit(f"An unexpected error occurred during thread execution: {e}")

# --- PyQt6 GUI Application ---
class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.downloader = Downloader() # Initialize downloader with default path
        self.download_thread = None
        self.initUI()
        self.load_settings() # Load last saved directory

    def initUI(self):
        self.setWindowTitle("Media Downloader")
        self.setGeometry(100, 100, 600, 350) # x, y, width, height
        self.setWindowIcon(QIcon(self._get_icon_path())) # Set application icon
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # URL Input
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Paste video/audio URL here (YouTube, Facebook, etc.)")
        self.url_input.setFixedHeight(30)
        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout)

        # Download Buttons
        button_layout = QHBoxLayout()
        self.video_button = QPushButton("Download Video", self)
        self.video_button.clicked.connect(lambda: self.start_download("video"))
        self.video_button.setFixedHeight(40)
        self.video_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(self.video_button)

        self.audio_button = QPushButton("Download Audio (m4a)", self)
        self.audio_button.clicked.connect(lambda: self.start_download("audio"))
        self.audio_button.setFixedHeight(40)
        self.audio_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        button_layout.addWidget(self.audio_button)
        main_layout.addLayout(button_layout)

        # Output Directory Selector
        output_layout = QHBoxLayout()
        self.output_dir_label = QLabel(f"Output: {self.downloader.output_path}", self)
        self.output_dir_label.setStyleSheet("font-style: italic; color: #555;")
        output_layout.addWidget(self.output_dir_label)

        self.output_dir_button = QPushButton("Change Folder", self)
        self.output_dir_button.clicked.connect(self.select_output_directory)
        self.output_dir_button.setFixedWidth(120)
        output_layout.addWidget(self.output_dir_button)
        main_layout.addLayout(output_layout)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
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
        main_layout.addWidget(self.progress_bar)

        # Status Label
        self.status_label = QLabel("Ready to download. Ensure FFmpeg is available.", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #333;")
        main_layout.addWidget(self.status_label)
        
        # Add a stretch to push content to top
        main_layout.addStretch()

        self.setLayout(main_layout)

    def _get_icon_path(self):
        # Look for icon.ico in the same directory as the script or bundled location
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
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
            settings_path = os.path.join(sys._MEIPASS, settings_file)
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
            settings_path = os.path.join(sys._MEIPASS, settings_file)
        else:
            settings_path = settings_file
            
        try:
            with open(settings_path, "w") as f:
                f.write(self.downloader.output_path)
        except Exception as e:
            print(f"Error saving settings: {e}")


    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if directory:
            self.downloader.output_path = directory
            self.output_dir_label.setText(f"Output: {directory}")
            self.status_label.setText(f"Download folder set to: {directory}")
            self.save_settings() # Save the new directory

    def start_download(self, download_type):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL to download.")
            return

        # Disable buttons during download
        self.video_button.setEnabled(False)
        self.audio_button.setEnabled(False)
        self.output_dir_button.setEnabled(False)
        self.url_input.setEnabled(False)

        self.status_label.setText(f"Starting {download_type} download...")
        self.progress_bar.setValue(0)

        # Create and start the download thread
        self.download_thread = DownloadThread(self.downloader, url, download_type)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.error_signal.connect(self.download_error)
        self.download_thread.start()

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
        elif d['status'] == 'error':
             self.status_label.setText(f"Download error: {d.get('error', 'Unknown error')}")


    def download_finished(self, message):
        self.status_label.setText(message)
        self.progress_bar.setValue(100)
        self._reset_ui_state()
        if "complete" in message.lower():
            QMessageBox.information(self, "Download Complete", message)
        else:
            QMessageBox.warning(self, "Download Status", message)


    def download_error(self, message):
        self.status_label.setText(f"Error: {message}")
        self._reset_ui_state()
        QMessageBox.critical(self, "Download Error", message)

    def _reset_ui_state(self):
        self.video_button.setEnabled(True)
        self.audio_button.setEnabled(True)
        self.output_dir_button.setEnabled(True)
        self.url_input.setEnabled(True)
        self.download_thread = None # Clear reference to the finished thread

if __name__ == '__main__':
    # Ensure sys.argv is correctly handled for PyInstaller bundles
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the search path to include the PyInstaller temporary
        # directory and the `ffmpeg` directory.
        # This makes sure os.path.abspath(__file__) returns the path to
        # the exe itself, not a temporary script in the bundle.
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Optional: Set the current working directory to the application path
    # This helps when looking for ffmpeg.exe or icon.ico
    os.chdir(application_path)

    app = QApplication(sys.argv)
    ex = DownloaderApp()
    ex.show()
    sys.exit(app.exec())