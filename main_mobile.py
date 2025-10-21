from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

class MediaDownloaderApp(App):
    def build(self):
        self.title = 'Media Downloader'
        
        # Main layout with tabs
        tab_panel = TabbedPanel(do_default_tab=False)
        
        # Download tab with enhanced styling
        download_tab = TabbedPanelItem(text='Download')
        download_tab.add_widget(self.create_download_layout())
        tab_panel.add_widget(download_tab)
        
        # Settings tab
        settings_tab = TabbedPanelItem(text='Settings')
        settings_tab.add_widget(self.create_settings_layout())
        tab_panel.add_widget(settings_tab)
        
        # History tab
        history_tab = TabbedPanelItem(text='History')
        history_tab.add_widget(self.create_history_layout())
        tab_panel.add_widget(history_tab)
        
        return tab_panel
    
    def create_download_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Title
        title_label = Label(
            text='Media Downloader', 
            size_hint_y=None, 
            height=40,
            color=(0.2, 0.6, 1, 1),  # Attractive blue color
            font_size='20sp',
            bold=True
        )
        layout.add_widget(title_label)
        
        # URL input with better styling
        url_label = Label(
            text='Enter Media URLs:', 
            size_hint_y=None, 
            height=30,
            color=(0.3, 0.3, 0.3, 1),
            font_size='16sp'
        )
        self.url_input = TextInput(
            multiline=True, 
            hint_text='Paste your media links here (one per line)\nWorks with YouTube, Facebook, Instagram, TikTok, Twitter, Vimeo, and many other platforms',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=(10, 10, 10, 10)
        )
        self.url_input.height = 120
        self.url_input.size_hint_y = None
        layout.add_widget(url_label)
        layout.add_widget(self.url_input)
        
        # Download buttons with improved colors
        button_layout = BoxLayout(size_hint_y=None, height=60, spacing=15)
        self.video_button = Button(
            text='Download Video', 
            background_color=(0.1, 0.7, 0.3, 1),  # Vibrant green
            color=(1, 1, 1, 1),
            bold=True,
            font_size='16sp'
        )
        self.video_button.bind(on_press=self.on_video_button_press)
        
        self.audio_button = Button(
            text='Download Audio', 
            background_color=(0.2, 0.5, 0.9, 1),  # Rich blue
            color=(1, 1, 1, 1),
            bold=True,
            font_size='16sp'
        )
        self.audio_button.bind(on_press=self.on_audio_button_press)
        
        button_layout.add_widget(self.video_button)
        button_layout.add_widget(self.audio_button)
        layout.add_widget(button_layout)
        
        # Progress bar with custom styling
        self.progress_bar = ProgressBar(
            max=100, 
            value=0, 
            size_hint_y=None, 
            height=35,
            color=(0.2, 0.7, 0.9, 1)  # Teal color
        )
        layout.add_widget(self.progress_bar)
        
        # Status label
        self.status_label = Label(
            text='Ready to download your media files.',
            color=(0.2, 0.2, 0.2, 1),
            font_size='15sp'
        )
        layout.add_widget(self.status_label)
        
        return layout
    
    def create_settings_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Title
        title_label = Label(
            text='Settings', 
            size_hint_y=None, 
            height=40,
            color=(0.2, 0.6, 1, 1),
            font_size='20sp',
            bold=True
        )
        layout.add_widget(title_label)
        
        # Settings content
        settings_label = Label(
            text='Settings will be available in the full implementation.\n\n'
                 'Customize your download experience:\n'
                 '• Video Quality\n'
                 '• Audio Format\n'
                 '• Download Location\n'
                 '• Network Settings',
            text_size=(None, None),
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        layout.add_widget(settings_label)
        
        return layout
    
    def create_history_layout(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Title
        title_label = Label(
            text='Download History', 
            size_hint_y=None, 
            height=40,
            color=(0.2, 0.6, 1, 1),
            font_size='20sp',
            bold=True
        )
        layout.add_widget(title_label)
        
        # History content
        history_label = Label(
            text='Your download history will appear here.\n\n'
                 'Track your downloaded media files,\n'
                 'view download status, and manage your content.',
            text_size=(None, None),
            halign='center',
            color=(0.3, 0.3, 0.3, 1)
        )
        layout.add_widget(history_label)
        
        return layout
    
    def on_video_button_press(self, instance):
        self.start_download('video')
    
    def on_audio_button_press(self, instance):
        self.start_download('audio')
    
    def start_download(self, download_type):
        urls_text = self.url_input.text.strip()
        if not urls_text:
            self.status_label.text = 'Please enter at least one URL to download.'
            self.status_label.color = (0.9, 0.2, 0.2, 1)  # Red for errors
            return
            
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # Disable UI during download
        self.video_button.disabled = True
        self.audio_button.disabled = True
        self.url_input.disabled = True
        
        # Reset progress
        self.progress_bar.value = 0
        self.status_label.text = f'Starting {download_type} download...'
        self.status_label.color = (0.2, 0.2, 0.2, 1)  # Default color
        
        # Start download in a separate thread
        import threading
        self.download_thread = threading.Thread(target=self.download_worker, args=(urls, download_type))
        self.download_thread.start()
    
    def download_worker(self, urls, download_type):
        try:
            total_urls = len(urls)
            for i, url in enumerate(urls):
                # Update status for current URL
                from kivy.clock import Clock
                Clock.schedule_once(
                    lambda dt, idx=i, u=url, total=total_urls: setattr(
                        self.status_label, 
                        'text', 
                        f'Downloading ({idx+1}/{total}): {u[:50]}{"..." if len(u) > 50 else ""}'
                    ), 0
                )
                
                # Simulate download progress
                for progress in range(101):
                    import time
                    time.sleep(0.02)  # Simulate work
                    # Update progress bar on main thread
                    from kivy.clock import Clock
                    Clock.schedule_once(
                        lambda dt, value=progress, idx=i, total=total_urls: setattr(
                            self.progress_bar, 
                            'value', 
                            int((idx * 100 + value) / total_urls)
                        ), 0
                    )
            
            # Update status on main thread when completed
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'All downloads completed successfully!'), 0)
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'color', (0.1, 0.7, 0.3, 1)), 0)  # Green for success
            Clock.schedule_once(lambda dt: setattr(self.video_button, 'disabled', False), 0)
            Clock.schedule_once(lambda dt: setattr(self.audio_button, 'disabled', False), 0)
            Clock.schedule_once(lambda dt: setattr(self.url_input, 'disabled', False), 0)
        except Exception as e:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.download_error(str(e)), 0)
    
    def download_error(self, error):
        self.status_label.text = f'Download failed: {error}'
        self.status_label.color = (0.9, 0.2, 0.2, 1)  # Red for errors
        self.video_button.disabled = False
        self.audio_button.disabled = False
        self.url_input.disabled = False

if __name__ == '__main__':
    MediaDownloaderApp().run()