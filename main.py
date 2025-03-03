#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubGen - AI Subtitle Generator
Main application window and entry point
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path
import time

import torch
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QSettings, QTimer, QSize, QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, 
    QProgressBar, QComboBox, QPushButton, QLabel, 
    QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QGroupBox,
    QCheckBox, QRadioButton, QButtonGroup, QFrame, QSplitter,
    QSizePolicy, QToolTip, QStyle, QAction
)

# Import our custom modules
from theme import Theme, ThemeManager
from components import DropArea, SubtitleEditor, CustomProgressBar
from transcription import WhisperTranscriptionThread
from utils import format_time, format_file_size, save_srt_to_vtt, ensure_directory


class SubtitleGenerator(QMainWindow):
    """Main application window for the SubGen subtitle generator"""
    
    def __init__(self):
        super().__init__()
        
        # State variables
        self.media_file = None
        self.audio_file = None
        self.subtitle_segments = []
        self.temp_dir = tempfile.TemporaryDirectory()
        self.settings = QSettings("SubGen", "AISubtitleGenerator")
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Set up the UI
        self.setup_ui()
        
        # Restore saved settings
        self.restore_settings()
        
        # Check for dependencies
        self.check_dependencies()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Window settings
        self.setWindowTitle("SubGen - AI Subtitle Generator")
        self.setMinimumSize(1000, 720)
        self.setWindowIcon(QIcon("icons/app_icon.png"))
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout - uses QVBoxLayout for top-to-bottom arrangement
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Add header with app name and theme toggle
        self.setup_header(main_layout)
        
        # Apply current theme (moved to after setup_header so self.theme_toggle exists)
        self.apply_theme()
        
        # Add main content area (file selection, settings, preview)
        self.setup_content_area(main_layout)
        
        # Set up status bar
        self.statusBar().showMessage("Ready")
        
        # Set up menu bar
        self.setup_menu()
    
    def setup_header(self, parent_layout):
        """Set up the application header with logo and controls"""
        header_layout = QHBoxLayout()
        
        # Logo and title
        app_logo = QLabel()
        icon_path = "icons/app_icon.png"
        if os.path.exists(icon_path):
            app_logo.setPixmap(QIcon(icon_path).pixmap(QSize(32, 32)))
        header_layout.addWidget(app_logo)
        
        app_title = QLabel("SubGen")
        app_title.setProperty("class", "app-title")
        header_layout.addWidget(app_title)
        
        app_subtitle = QLabel("AI Subtitle Generator")
        app_subtitle.setProperty("class", "app-subtitle")
        header_layout.addWidget(app_subtitle)
        
        header_layout.addStretch()
        
        # Theme toggle button
        self.theme_toggle = QPushButton()
        self.theme_toggle.setIcon(QIcon("icons/theme.png"))
        self.theme_toggle.setToolTip("Toggle Light/Dark Theme")
        self.theme_toggle.setProperty("class", "icon-button")
        self.theme_toggle.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_toggle)
        
        parent_layout.addLayout(header_layout)
    
    def setup_content_area(self, parent_layout):
        """Set up the main content area with file selection, settings, and preview"""
        # Create a layout for the content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left panel - Settings
        settings_panel = QWidget()
        settings_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        settings_panel.setMinimumWidth(380)
        settings_panel.setMaximumWidth(420)
        
        settings_layout = QVBoxLayout(settings_panel)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(15)
        
        # Add sections to settings panel
        self.setup_file_section(settings_layout)
        self.setup_language_section(settings_layout)
        self.setup_generation_section(settings_layout)
        self.setup_export_section(settings_layout)
        
        # Add stretch to push all content to the top
        settings_layout.addStretch()
        
        # Right panel - Preview
        preview_panel = QWidget()
        preview_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(15)
        
        self.setup_preview_section(preview_layout)
        
        # Add panels to content layout
        content_layout.addWidget(settings_panel)
        content_layout.addWidget(preview_panel)
        
        # Add content layout to main layout
        parent_layout.addLayout(content_layout, 1)  # The '1' gives this layout stretch priority
    
    def setup_file_section(self, parent_layout):
        """Set up the file selection section"""
        file_group = QGroupBox("1. Select Media File")
        file_group.setProperty("class", "card")
        
        file_layout = QVBoxLayout(file_group)
        file_layout.setContentsMargins(15, 25, 15, 15)
        file_layout.setSpacing(15)
        
        # Drop area for drag and drop
        self.drop_area = DropArea(self)
        self.drop_area.file_dropped.connect(self.handle_file_drop)
        file_layout.addWidget(self.drop_area)
        
        # Browse button
        browse_button = QPushButton("Browse Files")
        browse_button.setProperty("class", "primary-button")
        browse_button.setIcon(QIcon("icons/browse.png"))
        browse_button.setCursor(Qt.PointingHandCursor)
        browse_button.clicked.connect(self.browse_files)
        file_layout.addWidget(browse_button)
        
        # File info
        self.file_info = QLabel("No file selected")
        self.file_info.setWordWrap(True)
        self.file_info.setProperty("class", "file-info")
        file_layout.addWidget(self.file_info)
        
        parent_layout.addWidget(file_group)
    
    def setup_language_section(self, parent_layout):
        """Set up the language selection section"""
        language_group = QGroupBox("2. Language Settings")
        language_group.setProperty("class", "card")
        
        language_layout = QVBoxLayout(language_group)
        language_layout.setContentsMargins(15, 25, 15, 15)
        language_layout.setSpacing(15)
        
        # Source language selection
        source_layout = QHBoxLayout()
        source_label = QLabel("Source Language:")
        source_label.setProperty("class", "form-label")
        source_layout.addWidget(source_label)
        
        self.source_language_combo = QComboBox()
        self.source_language_combo.setProperty("class", "combo-box")
        
        # Add common languages
        languages = [
            ("Auto Detect", "auto"),
            ("English", "en"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de"),
            ("Italian", "it"),
            ("Portuguese", "pt"),
            ("Romanian", "ro"),
            ("Russian", "ru"),
            ("Chinese", "zh"),
            ("Japanese", "ja"),
            ("Korean", "ko")
        ]
        
        for name, code in languages:
            self.source_language_combo.addItem(name, code)
        
        source_layout.addWidget(self.source_language_combo)
        language_layout.addLayout(source_layout)
        
        # Transcription mode (transcribe only or translate)
        self.transcribe_radio = QRadioButton("Transcribe only")
        self.transcribe_radio.setProperty("class", "radio-button")
        self.translate_radio = QRadioButton("Translate to:")
        self.translate_radio.setProperty("class", "radio-button")
        
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.transcribe_radio, 1)
        self.mode_group.addButton(self.translate_radio, 2)
        self.transcribe_radio.setChecked(True)
        
        language_layout.addWidget(self.transcribe_radio)
        
        # Target language (for translation)
        target_layout = QHBoxLayout()
        target_layout.addWidget(self.translate_radio)
        
        self.target_language_combo = QComboBox()
        self.target_language_combo.setProperty("class", "combo-box")
        self.target_language_combo.setEnabled(False)
        
        # Connect radio buttons to enable/disable target language
        self.translate_radio.toggled.connect(lambda checked: self.target_language_combo.setEnabled(checked))
        
        # Add languages supported by LibreTranslate
        target_languages = [
            ("English", "en"),
            ("Arabic", "ar"),
            ("Chinese", "zh"),
            ("French", "fr"),
            ("German", "de"),
            ("Hindi", "hi"),
            ("Italian", "it"),
            ("Japanese", "ja"),
            ("Korean", "ko"),
            ("Portuguese", "pt"),
            ("Romanian", "ro"),
            ("Russian", "ru"),
            ("Spanish", "es")
        ]
        
        for name, code in target_languages:
            self.target_language_combo.addItem(name, code)
            
        target_layout.addWidget(self.target_language_combo)
        language_layout.addLayout(target_layout)
        
        # Translation note
        translation_note = QLabel("Translation uses LibreTranslate (free service). If translation fails, original text will be kept.")
        translation_note.setWordWrap(True)
        translation_note.setProperty("class", "note-text")
        language_layout.addWidget(translation_note)
        
        parent_layout.addWidget(language_group)
    
    def setup_generation_section(self, parent_layout):
        """Set up the subtitle generation section"""
        generate_group = QGroupBox("3. Generate Subtitles")
        generate_group.setProperty("class", "card")
        
        generate_layout = QVBoxLayout(generate_group)
        generate_layout.setContentsMargins(15, 25, 15, 15)
        generate_layout.setSpacing(15)
        
        # Generate button
        self.generate_button = QPushButton("Generate Subtitles")
        self.generate_button.setProperty("class", "accent-button")
        self.generate_button.setIcon(QIcon("icons/generate.png"))
        self.generate_button.setEnabled(False)
        self.generate_button.setCursor(Qt.PointingHandCursor)
        self.generate_button.clicked.connect(self.generate_subtitles)
        generate_layout.addWidget(self.generate_button)
        
        # Cancel button (hidden by default)
        self.cancel_button = QPushButton("Cancel Generation")
        self.cancel_button.setProperty("class", "danger-button")
        self.cancel_button.setVisible(False)
        self.cancel_button.clicked.connect(self.cancel_generation)
        generate_layout.addWidget(self.cancel_button)
        
        # Progress section
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)
        
        # Custom progress bar with animations
        self.progress_bar = CustomProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        # Progress status label
        self.progress_label = QLabel()
        self.progress_label.setWordWrap(True)
        self.progress_label.setProperty("class", "status-text")
        self.progress_label.setVisible(False)
        progress_layout.addWidget(self.progress_label)
        
        # Time remaining label
        self.time_label = QLabel()
        self.time_label.setProperty("class", "time-text")
        self.time_label.setVisible(False)
        progress_layout.addWidget(self.time_label)
        
        generate_layout.addWidget(progress_container)
        
        parent_layout.addWidget(generate_group)
    
    def setup_export_section(self, parent_layout):
        """Set up the export options section"""
        export_group = QGroupBox("4. Save & Export")
        export_group.setProperty("class", "card")
        
        export_layout = QVBoxLayout(export_group)
        export_layout.setContentsMargins(15, 25, 15, 15)
        export_layout.setSpacing(15)
        
        # SRT and VTT export buttons
        button_grid = QHBoxLayout()
        
        self.save_srt_button = QPushButton("Save as SRT")
        self.save_srt_button.setProperty("class", "primary-button")
        self.save_srt_button.setIcon(QIcon("icons/srt.png"))
        self.save_srt_button.setEnabled(False)
        self.save_srt_button.setCursor(Qt.PointingHandCursor)
        self.save_srt_button.clicked.connect(lambda: self.save_subtitles(".srt"))
        button_grid.addWidget(self.save_srt_button)
        
        self.save_vtt_button = QPushButton("Save as VTT")
        self.save_vtt_button.setProperty("class", "primary-button")
        self.save_vtt_button.setIcon(QIcon("icons/vtt.png"))
        self.save_vtt_button.setEnabled(False)
        self.save_vtt_button.setCursor(Qt.PointingHandCursor)
        self.save_vtt_button.clicked.connect(lambda: self.save_subtitles(".vtt"))
        button_grid.addWidget(self.save_vtt_button)
        
        export_layout.addLayout(button_grid)
        
        # Embed subtitles button
        self.embed_button = QPushButton("Embed into Video")
        self.embed_button.setProperty("class", "secondary-button")
        self.embed_button.setIcon(QIcon("icons/embed.png"))
        self.embed_button.setEnabled(False)
        self.embed_button.setCursor(Qt.PointingHandCursor)
        self.embed_button.clicked.connect(self.embed_subtitles)
        export_layout.addWidget(self.embed_button)
        
        parent_layout.addWidget(export_group)
    
    def setup_preview_section(self, parent_layout):
        """Set up the subtitle preview and editing section"""
        # Header with title and format selector
        header_layout = QHBoxLayout()
        
        preview_title = QLabel("Subtitle Preview & Editor")
        preview_title.setProperty("class", "section-title")
        header_layout.addWidget(preview_title)
        
        header_layout.addStretch()
        
        # Format selection
        format_label = QLabel("Format:")
        format_label.setProperty("class", "form-label")
        header_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.setProperty("class", "combo-box")
        self.format_combo.addItem("SRT", "srt")
        self.format_combo.addItem("VTT", "vtt")
        self.format_combo.setFixedWidth(100)
        # TODO: Implement format switching
        header_layout.addWidget(self.format_combo)
        
        parent_layout.addLayout(header_layout)
        
        # Placeholder when no subtitles
        self.placeholder = QLabel("Generate subtitles to see them here")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setProperty("class", "placeholder")
        parent_layout.addWidget(self.placeholder)
        
        # Modern subtitle editor with individual segments
        self.subtitle_editor = SubtitleEditor()
        self.subtitle_editor.setVisible(False)
        parent_layout.addWidget(self.subtitle_editor)
        
        # Basic text editor for compatibility
        self.subtitle_preview = QTextEdit()
        self.subtitle_preview.setPlaceholderText("Subtitles will appear here after generation")
        self.subtitle_preview.setProperty("class", "text-edit")
        self.subtitle_preview.setVisible(False)
        parent_layout.addWidget(self.subtitle_preview)
    
    def setup_menu(self):
        """Set up the application menu"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        open_action = QAction("Open Media File...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.browse_files)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_srt_action = QAction("Save as SRT...", self)
        save_srt_action.setShortcut("Ctrl+S")
        save_srt_action.triggered.connect(lambda: self.save_subtitles(".srt"))
        file_menu.addAction(save_srt_action)
        
        save_vtt_action = QAction("Save as VTT...", self)
        save_vtt_action.setShortcut("Ctrl+Shift+S")
        save_vtt_action.triggered.connect(lambda: self.save_subtitles(".vtt"))
        file_menu.addAction(save_vtt_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menu_bar.addMenu("Settings")
        
        theme_action = QAction("Toggle Dark Mode", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)
        settings_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction("About SubGen", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        check_deps_action = QAction("Check Dependencies", self)
        check_deps_action.triggered.connect(lambda: self.check_dependencies(show_success=True))
        help_menu.addAction(check_deps_action)
    
    def apply_theme(self):
        """Apply the current theme to the application"""
        # Get current theme stylesheet
        stylesheet = self.theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)
        
        # Update icon for theme toggle
        if self.theme_manager.is_dark_mode():
            self.theme_toggle.setIcon(QIcon("icons/light_mode.png"))
            self.theme_toggle.setToolTip("Switch to Light Mode")
        else:
            self.theme_toggle.setIcon(QIcon("icons/dark_mode.png"))
            self.theme_toggle.setToolTip("Switch to Dark Mode")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme_manager.toggle_theme()
        self.apply_theme()
        self.settings.setValue("dark_mode", self.theme_manager.is_dark_mode())
    
    def restore_settings(self):
        """Restore user settings"""
        # Restore theme
        dark_mode = self.settings.value("dark_mode", False, type=bool)
        if dark_mode:
            self.theme_manager.set_dark_mode(True)
            self.apply_theme()
        
        # Restore source language
        source_lang = self.settings.value("source_language", "en")
        index = self.source_language_combo.findData(source_lang)
        if index >= 0:
            self.source_language_combo.setCurrentIndex(index)
        
        # Restore translation settings
        translate = self.settings.value("translate", False, type=bool)
        if translate:
            self.translate_radio.setChecked(True)
            
            # Restore target language
            target_lang = self.settings.value("target_language", "en")
            index = self.target_language_combo.findData(target_lang)
            if index >= 0:
                self.target_language_combo.setCurrentIndex(index)
    
    def save_settings(self):
        """Save current settings"""
        # Save language settings
        self.settings.setValue("source_language", self.source_language_combo.currentData())
        self.settings.setValue("translate", self.translate_radio.isChecked())
        self.settings.setValue("target_language", self.target_language_combo.currentData())
        
        # Save theme setting
        self.settings.setValue("dark_mode", self.theme_manager.is_dark_mode())
    
    def check_dependencies(self, show_success=False):
        """Check if required dependencies are installed"""
        missing_deps = []
        
        try:
            # Check for FFmpeg
            process = subprocess.run(
                ["ffmpeg", "-version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            if process.returncode != 0:
                missing_deps.append("FFmpeg")
            
            # Check for PyTorch
            if not torch.__version__:
                missing_deps.append("PyTorch")
            
            # Check for CUDA (optional, for faster processing)
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                self.statusBar().showMessage(f"GPU detected: {gpu_name}")
            else:
                self.statusBar().showMessage("CUDA not available. Using CPU for processing (slower).")
            
            # Show message if dependencies are missing
            if missing_deps:
                message = "The following dependencies are missing:\n"
                for dep in missing_deps:
                    message += f"- {dep}\n"
                message += "\nSome features may not work correctly."
                QMessageBox.warning(self, "Missing Dependencies", message)
            elif show_success:
                QMessageBox.information(
                    self, 
                    "Dependencies Check", 
                    "All required dependencies are installed!\n\n" +
                    ("Using GPU acceleration: " + gpu_name if torch.cuda.is_available() 
                     else "Using CPU mode (slower). Consider using a system with GPU support for faster processing.")
                )
                
        except Exception as e:
            QMessageBox.warning(self, "Dependency Check Failed", str(e))
    
    def browse_files(self):
        """Open file browser to select media file"""
        file_filter = "Media Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.mp3 *.wav *.aac *.flac *.ogg *.eac3)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Media File", "", file_filter
        )
        
        if file_path:
            self.process_selected_file(file_path)
    
    def handle_file_drop(self, file_path):
        """Handle file dropped via drag and drop"""
        self.process_selected_file(file_path)
    
    def process_selected_file(self, file_path):
        """Process the selected media file"""
        self.media_file = file_path
        file_name = os.path.basename(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Determine file type (audio or video)
        audio_extensions = ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.eac3']
        is_audio = file_ext in audio_extensions
        
        # Update UI with file info
        info_text = (
            f"<b>File:</b> {file_name}<br>"
            f"<b>Size:</b> {format_file_size(file_size)}<br>"
            f"<b>Type:</b> {'Audio' if is_audio else 'Video'} ({file_ext})"
        )
        self.file_info.setText(info_text)
        
        # Enable generate button
        self.generate_button.setEnabled(True)
        
        self.statusBar().showMessage(f"File loaded: {file_name}")
    
    def generate_subtitles(self):
        """Start the subtitle generation process"""
        if not self.media_file:
            QMessageBox.warning(self, "Error", "Please select a file first")
            return
        
        # Save current settings
        self.save_settings()
        
        # Update UI for generation process
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.time_label.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Preparing...")
        self.time_label.setText("")
        
        self.generate_button.setVisible(False)
        self.cancel_button.setVisible(True)
        
        self.save_srt_button.setEnabled(False)
        self.save_vtt_button.setEnabled(False)
        self.embed_button.setEnabled(False)
        
        # Hide editors, show placeholder with "Processing" message
        self.subtitle_editor.setVisible(False)
        self.subtitle_preview.setVisible(False)
        self.placeholder.setText("Processing... Please wait")
        self.placeholder.setVisible(True)
        
        # Set start time for estimation
        self.start_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_estimate)
        self.timer.start(1000)  # Update every second
        
        # Extract audio if needed
        self.extract_audio()
    
    def update_time_estimate(self):
        """Update the estimated time remaining"""
        elapsed = time.time() - self.start_time
        if elapsed < 2:  # Don't show estimates too early
            return
            
        # Get current progress
        progress = self.progress_bar.value()
        if progress <= 0:
            return
            
        # Estimate remaining time
        remaining = (elapsed / progress) * (100 - progress)
        
        if remaining > 0:
            self.time_label.setText(f"Estimated time remaining: {format_time(remaining)}")
    
    def cancel_generation(self):
        """Cancel the ongoing generation process"""
        if hasattr(self, 'transcription_thread') and self.transcription_thread.isRunning():
            self.transcription_thread.cancel()
            self.transcription_thread.wait()
        
        # Stop timer
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
            
        self.statusBar().showMessage("Generation cancelled")
        self.reset_ui()
    
    def extract_audio(self):
        """Extract audio from video file if needed"""
        file_ext = os.path.splitext(self.media_file)[1].lower()
        
        # Check if the file is already an audio file
        audio_extensions = ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.eac3']
        if file_ext in audio_extensions:
            self.audio_file = self.media_file
            self.start_transcription()
            return
            
        # Extract audio using FFmpeg
        try:
            self.progress_label.setText("Extracting audio from video...")
            self.progress_bar.setValue(5)
            
            # Ensure temp directory exists
            temp_dir = Path(self.temp_dir.name)
            ensure_directory(temp_dir)
            
            output_audio = temp_dir / "audio.wav"
            
            process = subprocess.run(
                [
                    "ffmpeg", "-i", self.media_file, 
                    "-vn", "-acodec", "pcm_s16le", 
                    "-ar", "16000", "-ac", "1",
                    str(output_audio), "-y"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if process.returncode != 0:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to extract audio: {process.stderr.decode()}"
                )
                self.reset_ui()
                return
                
            self.audio_file = str(output_audio)
            self.start_transcription()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process audio: {str(e)}")
            self.reset_ui()
    
    def start_transcription(self):
        """Start the Whisper transcription process"""
        if not self.audio_file:
            QMessageBox.warning(self, "Error", "Audio extraction failed")
            self.reset_ui()
            return
            
        # Get selected language settings
        source_language = self.source_language_combo.currentData()
        translate = self.translate_radio.isChecked()
        target_language = self.target_language_combo.currentData() if translate else None
        
        # Status message
        if translate:
            target_lang_name = self.target_language_combo.currentText()
            self.statusBar().showMessage(f"Transcribing and translating to {target_lang_name}... This may take a while")
        else:
            self.statusBar().showMessage("Transcribing audio... This may take a while")
        
        # Create and start the transcription thread
        self.transcription_thread = WhisperTranscriptionThread(
            self.audio_file, 
            source_language,
            translate,
            target_language
        )
        
        self.transcription_thread.progress_update.connect(self.update_progress)
        self.transcription_thread.transcription_complete.connect(self.handle_transcription_complete)
        self.transcription_thread.error_occurred.connect(self.handle_transcription_error)
        
        self.transcription_thread.start()
    
    def update_progress(self, value, message):
        """Update progress bar and message"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        
        # Update application to ensure UI is responsive
        QApplication.processEvents()
    
    def handle_transcription_complete(self, segments):
        """Process completed transcription"""
        # Stop timer
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
            
        self.subtitle_segments = segments
        
        # Display in modern segment editor
        self.subtitle_editor.set_segments(segments)
        self.subtitle_editor.setVisible(True)
        
        # Also update traditional text preview for backward compatibility
        preview_text = ""
        for i, segment in enumerate(segments, 1):
            preview_text += f"{i}\n{segment['start']} --> {segment['end']}\n{segment['text']}\n\n"
        
        self.subtitle_preview.setText(preview_text)
        
        # Hide placeholder
        self.placeholder.setVisible(False)
        
        # Update UI state
        self.save_srt_button.setEnabled(True)
        self.save_vtt_button.setEnabled(True)
        
        # Enable embed button only for video files
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv']
        if os.path.splitext(self.media_file)[1].lower() in video_extensions:
            self.embed_button.setEnabled(True)
        
        # Reset UI
        self.generate_button.setVisible(True)
        self.cancel_button.setVisible(False)
        self.generate_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.time_label.setVisible(False)
        
        # Update status message
        if self.translate_radio.isChecked():
            self.statusBar().showMessage(f"Translation complete! You can now save or edit the subtitles.")
        else:
            self.statusBar().showMessage("Transcription complete! You can now save or edit the subtitles.")
    
    def handle_transcription_error(self, error_message):
        """Handle errors during transcription"""
        # Stop timer
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
            
        QMessageBox.critical(self, "Transcription Error", error_message)
        self.reset_ui()
    
    def save_subtitles(self, format_ext):
        """Save subtitles to a file"""
        if not self.subtitle_segments:
            QMessageBox.warning(self, "Error", "No subtitles to save")
            return
            
        # Get the base filename without extension
        base_name = os.path.splitext(os.path.basename(self.media_file))[0]
        
        # Add language indicator to filename if translating
        if self.translate_radio.isChecked():
            target_lang = self.target_language_combo.currentData()
            default_filename = f"{base_name}_{target_lang}{format_ext}"
        else:
            source_lang = self.source_language_combo.currentData()
            if source_lang != "auto":
                default_filename = f"{base_name}_{source_lang}{format_ext}"
            else:
                default_filename = f"{base_name}{format_ext}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            f"Save Subtitles as {format_ext}", 
            default_filename, 
            f"Subtitle Files (*{format_ext})"
        )
        
        if not file_path:
            return
            
        try:
            # Get subtitle content based on active editor
            if self.subtitle_editor.isVisible():
                srt_content = self.subtitle_editor.get_srt_content()
            else:
                srt_content = self.subtitle_preview.toPlainText()
            
            # Convert to VTT if needed
            if format_ext.lower() == ".vtt":
                content = save_srt_to_vtt(srt_content)
            else:
                content = srt_content
                
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            QMessageBox.information(
                self, 
                "Success", 
                f"Subtitles saved to {file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to save subtitles: {str(e)}"
            )
    
    def embed_subtitles(self):
        """Embed subtitles into video file"""
        if not self.subtitle_segments or not self.media_file:
            QMessageBox.warning(self, "Error", "No subtitles or video to embed")
            return
            
        # First save the SRT file temporarily
        temp_dir = Path(self.temp_dir.name)
        ensure_directory(temp_dir)
        temp_srt = temp_dir / "subtitles.srt"
        
        try:
            # Get subtitle content
            if self.subtitle_editor.isVisible():
                srt_content = self.subtitle_editor.get_srt_content()
            else:
                srt_content = self.subtitle_preview.toPlainText()
            
            with open(temp_srt, 'w', encoding='utf-8') as f:
                f.write(srt_content)
                
            # Get output filename
            base_name = os.path.splitext(os.path.basename(self.media_file))[0]
            
            # Add language indicator to filename if translating
            if self.translate_radio.isChecked():
                target_lang = self.target_language_combo.currentData()
                default_output = f"{base_name}_{target_lang}_subtitled.mp4"
            else:
                source_lang = self.source_language_combo.currentData()
                if source_lang != "auto":
                    default_output = f"{base_name}_{source_lang}_subtitled.mp4"
                else:
                    default_output = f"{base_name}_subtitled.mp4"
            
            output_file, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Video with Subtitles", 
                default_output, 
                "Video Files (*.mp4)"
            )
            
            if not output_file:
                return
            
            # Ask user if they want soft (default) or hard subtitles
            subtitle_type = QMessageBox.question(
                self,
                "Subtitle Type",
                "Do you want to burn subtitles into the video (hardcoded)?\n\n"
                "Yes = Burned into video (can't be turned off)\n"
                "No = Soft subtitles (can be turned on/off)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_label.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_label.setText("Embedding subtitles into video. This may take a while...")
            self.statusBar().showMessage("Embedding subtitles... This may take a while")
            
            # Update UI to show processing
            QApplication.processEvents()
            
            # Start FFmpeg process in a way that allows us to track progress
            if subtitle_type == QMessageBox.Yes:
                # Hardcoded subtitles
                command = [
                    "ffmpeg", "-i", self.media_file,
                    "-vf", f"subtitles={temp_srt}",
                    "-c:a", "copy", output_file, "-y"
                ]
            else:
                # Soft subtitles
                command = [
                    "ffmpeg", "-i", self.media_file,
                    "-i", str(temp_srt), "-c", "copy", 
                    "-c:s", "mov_text", output_file, "-y"
                ]
            
            # Execute the command
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Simple animation while processing
            progress = 0
            while process.poll() is None:
                progress = (progress + 1) % 100
                self.progress_bar.setValue(progress)
                QApplication.processEvents()
                time.sleep(0.01)
            
            # Check result
            if process.returncode != 0:
                stderr = process.stderr.read()
                raise Exception(f"FFmpeg error: {stderr}")
            
            # Hide progress
            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(False)
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Video with subtitles saved to {output_file}"
            )
            
            self.statusBar().showMessage("Video saved successfully!")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(False)
            
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to embed subtitles: {str(e)}"
            )
            self.statusBar().showMessage("Failed to embed subtitles")
    
    def reset_ui(self):
        """Reset UI elements after error or completion"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.time_label.setVisible(False)
        self.progress_bar.setValue(0)
        
        self.generate_button.setVisible(True)
        self.cancel_button.setVisible(False)
        self.generate_button.setEnabled(True if self.media_file else False)
        
        # Reset placeholder text
        self.placeholder.setText("Generate subtitles to see them here")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About SubGen",
            """<h1>SubGen - AI Subtitle Generator</h1>
            <p>Version 1.1.0</p>
            <p>A simple, easy-to-use AI-powered subtitle generator using OpenAI's Whisper model.</p>
            <p>Features:</p>
            <ul>
                <li>Automatic transcription with Whisper AI</li>
                <li>Multi-language support</li>
                <li>Translation capabilities</li>
                <li>SRT and VTT export</li>
                <li>Direct subtitle embedding</li>
                <li>Modern user interface</li>
            </ul>
            <p>Copyright © 2023-2025</p>"""
        )
    
    def closeEvent(self, event):
        """Clean up resources before closing"""
        # Save settings
        self.save_settings()
        
        # Clean up temporary directory
        if hasattr(self, 'temp_dir'):
            self.temp_dir.cleanup()
        
        event.accept()


def main():
    # Enable High DPI scaling
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application icon
    if os.path.exists("icons/app_icon.png"):
        app.setWindowIcon(QIcon("icons/app_icon.png"))
    
    # Create and show main window
    window = SubtitleGenerator()
    window.show()
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()