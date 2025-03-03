#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubGen - AI Subtitle Generator
Theme management and styling
"""

from PyQt5.QtCore import QObject, QSettings

class Theme:
    """Class containing theme color constants"""
    
    # Light theme colors
    LIGHT = {
        # Primary colors
        'primary': '#3498db',
        'primary_hover': '#2980b9',
        'primary_pressed': '#1f6dad',
        
        'secondary': '#2ecc71',
        'secondary_hover': '#27ae60',
        'secondary_pressed': '#219a52',
        
        'danger': '#e74c3c',
        'danger_hover': '#c0392b',
        'danger_pressed': '#a93226',
        
        'warning': '#f39c12',
        'warning_hover': '#d35400',
        
        'success': '#2ecc71',
        
        # Background colors
        'background': '#f5f6fa',
        'card': '#ffffff',
        'input_bg': '#ffffff',
        
        # Text colors
        'text': '#2c3e50',
        'text_secondary': '#7f8c8d',
        'text_light': '#ffffff',
        'placeholder': '#95a5a6',
        
        # Border colors
        'border': '#e0e0e0',
        'border_hover': '#3498db',
        
        # States
        'disabled': '#bdc3c7',
        'disabled_text': '#95a5a6',
        
        # Special elements
        'progress_bg': '#ecf0f1',
        'progress_fill': '#2ecc71',
        'highlight': '#3498db',
        'selection': 'rgba(52, 152, 219, 0.2)',
        'hover_overlay': 'rgba(0, 0, 0, 0.05)',
        'shadow': 'rgba(0, 0, 0, 0.1)'
    }
    
    # Dark theme colors
    DARK = {
        # Primary colors
        'primary': '#3498db',
        'primary_hover': '#2980b9',
        'primary_pressed': '#1f6dad',
        
        'secondary': '#2ecc71',
        'secondary_hover': '#27ae60',
        'secondary_pressed': '#219a52',
        
        'danger': '#e74c3c',
        'danger_hover': '#c0392b',
        'danger_pressed': '#a93226',
        
        'warning': '#f39c12',
        'warning_hover': '#d35400',
        
        'success': '#27ae60',
        
        # Background colors
        'background': '#1e1e2e',
        'card': '#2a2a3c',
        'input_bg': '#303046',
        
        # Text colors
        'text': '#ecf0f1',
        'text_secondary': '#95a5a6',
        'text_light': '#ffffff',
        'placeholder': '#7f8c8d',
        
        # Border colors
        'border': '#3f3f5f',
        'border_hover': '#3498db',
        
        # States
        'disabled': '#3f3f5f',
        'disabled_text': '#7f8c8d',
        
        # Special elements
        'progress_bg': '#303046',
        'progress_fill': '#2ecc71',
        'highlight': '#3498db',
        'selection': 'rgba(52, 152, 219, 0.3)',
        'hover_overlay': 'rgba(255, 255, 255, 0.05)',
        'shadow': 'rgba(0, 0, 0, 0.3)'
    }


class ThemeManager(QObject):
    """Theme manager for the application"""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("SubGen", "AISubtitleGenerator")
        self.dark_mode = self.settings.value("dark_mode", False, type=bool)
    
    def is_dark_mode(self):
        """Check if dark mode is enabled"""
        return self.dark_mode
    
    def set_dark_mode(self, enabled):
        """Set dark mode state"""
        self.dark_mode = enabled
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.dark_mode = not self.dark_mode
    
    def get_current_theme(self):
        """Get the current theme colors"""
        return Theme.DARK if self.dark_mode else Theme.LIGHT
    
    def get_color(self, name):
        """Get a specific color from the current theme"""
        theme = self.get_current_theme()
        return theme.get(name, "#000000")  # Return black as fallback
    
    def get_stylesheet(self):
        """Get the full stylesheet for the current theme"""
        theme = self.get_current_theme()
        
        # Application-wide stylesheet
        stylesheet = f"""
            /* Global Styles */
            QWidget {{
                color: {theme['text']};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                font-size: 14px;
            }}
            
            QMainWindow {{
                background-color: {theme['background']};
            }}
            
            QDialog {{
                background-color: {theme['background']};
            }}
            
            /* Text Styling */
            QLabel {{
                color: {theme['text']};
            }}
            
            QLabel[class="app-title"] {{
                color: {theme['primary']};
                font-size: 22px;
                font-weight: bold;
            }}
            
            QLabel[class="app-subtitle"] {{
                color: {theme['text_secondary']};
                font-size: 16px;
            }}
            
            QLabel[class="section-title"] {{
                color: {theme['primary']};
                font-size: 16px;
                font-weight: bold;
            }}
            
            QLabel[class="form-label"] {{
                color: {theme['text']};
                font-size: 14px;
            }}
            
            QLabel[class="status-text"] {{
                color: {theme['text']};
                font-size: 13px;
            }}
            
            QLabel[class="time-text"] {{
                color: {theme['text_secondary']};
                font-size: 12px;
                font-style: italic;
            }}
            
            QLabel[class="note-text"] {{
                color: {theme['text_secondary']};
                font-size: 12px;
                font-style: italic;
                background-color: {theme['background']};
                border-radius: 4px;
                padding: 8px;
            }}
            
            QLabel[class="file-info"] {{
                color: {theme['text_secondary']};
                padding: 5px;
            }}
            
            /* Placeholder */
            QLabel[class="placeholder"] {{
                color: {theme['placeholder']};
                font-size: 16px;
                border: 2px dashed {theme['border']};
                border-radius: 8px;
                padding: 40px;
                background-color: {theme['card']};
            }}
            
            /* Cards */
            QGroupBox[class="card"] {{
                background-color: {theme['card']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding-top: 30px;
                margin-top: 16px;
                font-weight: bold;
                font-size: 15px;
            }}
            
            QGroupBox[class="card"]::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                top: 8px;
                padding: 0 5px;
                color: {theme['primary']};
            }}
            
            /* Buttons */
            QPushButton[class="primary-button"] {{
                background-color: {theme['primary']};
                color: {theme['text_light']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
                min-height: 36px;
            }}
            
            QPushButton[class="primary-button"]:hover {{
                background-color: {theme['primary_hover']};
            }}
            
            QPushButton[class="primary-button"]:pressed {{
                background-color: {theme['primary_pressed']};
            }}
            
            QPushButton[class="primary-button"]:disabled {{
                background-color: {theme['disabled']};
                color: {theme['disabled_text']};
            }}
            
            QPushButton[class="accent-button"] {{
                background-color: {theme['secondary']};
                color: {theme['text_light']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
                min-height: 36px;
            }}
            
            QPushButton[class="accent-button"]:hover {{
                background-color: {theme['secondary_hover']};
            }}
            
            QPushButton[class="accent-button"]:pressed {{
                background-color: {theme['secondary_pressed']};
            }}
            
            QPushButton[class="accent-button"]:disabled {{
                background-color: {theme['disabled']};
                color: {theme['disabled_text']};
            }}
            
            QPushButton[class="secondary-button"] {{
                background-color: {theme['card']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
                min-height: 36px;
            }}
            
            QPushButton[class="secondary-button"]:hover {{
                background-color: {theme['hover_overlay']};
                border-color: {theme['primary']};
            }}
            
            QPushButton[class="secondary-button"]:pressed {{
                background-color: {theme['selection']};
            }}
            
            QPushButton[class="secondary-button"]:disabled {{
                color: {theme['disabled_text']};
                border-color: {theme['disabled']};
            }}
            
            QPushButton[class="danger-button"] {{
                background-color: {theme['danger']};
                color: {theme['text_light']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
                min-height: 36px;
            }}
            
            QPushButton[class="danger-button"]:hover {{
                background-color: {theme['danger_hover']};
            }}
            
            QPushButton[class="danger-button"]:pressed {{
                background-color: {theme['danger_pressed']};
            }}
            
            QPushButton[class="icon-button"] {{
                background-color: transparent;
                border: none;
                border-radius: 15px;
                padding: 5px;
            }}
            
            QPushButton[class="icon-button"]:hover {{
                background-color: {theme['hover_overlay']};
            }}
            
            QPushButton[class="icon-button"]:pressed {{
                background-color: {theme['selection']};
            }}
            
            /* Combo Box */
            QComboBox[class="combo-box"] {{
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 6px 12px;
                background-color: {theme['input_bg']};
                color: {theme['text']};
                min-height: 36px;
                font-size: 14px;
            }}
            
            QComboBox[class="combo-box"]:hover {{
                border-color: {theme['border_hover']};
            }}
            
            QComboBox[class="combo-box"]:focus {{
                border: 2px solid {theme['primary']};
            }}
            
            QComboBox[class="combo-box"]::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border: none;
            }}
            
            QComboBox[class="combo-box"] QAbstractItemView {{
                border: 1px solid {theme['border']};
                border-radius: 6px;
                background-color: {theme['input_bg']};
                selection-background-color: {theme['primary']};
                selection-color: {theme['text_light']};
            }}
            
            QComboBox[class="combo-box"]:disabled {{
                background-color: {theme['disabled']};
                color: {theme['disabled_text']};
            }}
            
            /* Radio Buttons */
            QRadioButton[class="radio-button"] {{
                spacing: 8px;
                color: {theme['text']};
                font-size: 14px;
            }}
            
            QRadioButton[class="radio-button"]::indicator {{
                width: 20px;
                height: 20px;
            }}
            
            QRadioButton[class="radio-button"]::indicator:unchecked {{
                border: 2px solid {theme['border']};
                border-radius: 10px;
                background-color: {theme['input_bg']};
            }}
            
            QRadioButton[class="radio-button"]::indicator:checked {{
                border: 2px solid {theme['primary']};
                border-radius: 10px;
                background-color: {theme['primary']};
            }}
            
            QRadioButton[class="radio-button"]:hover {{
                color: {theme['primary']};
            }}
            
            /* Text Edit */
            QTextEdit[class="text-edit"] {{
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 12px;
                background-color: {theme['input_bg']};
                color: {theme['text']};
                font-size: 14px;
                line-height: 1.5;
            }}
            
            QTextEdit[class="text-edit"]:focus {{
                border: 2px solid {theme['primary']};
            }}
            
            /* Progress Bar */
            QProgressBar {{
                border: none;
                border-radius: 4px;
                text-align: center;
                background-color: {theme['progress_bg']};
                color: {theme['text']};
                font-weight: bold;
                font-size: 13px;
                height: 16px;
            }}
            
            QProgressBar::chunk {{
                background-color: {theme['progress_fill']};
                border-radius: 4px;
            }}
            
            /* Menu Bar */
            QMenuBar {{
                background-color: {theme['card']};
                color: {theme['text']};
                border-bottom: 1px solid {theme['border']};
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 10px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {theme['selection']};
                border-radius: 4px;
            }}
            
            QMenu {{
                background-color: {theme['card']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                padding: 5px 0px;
            }}
            
            QMenu::item {{
                padding: 6px 25px 6px 20px;
            }}
            
            QMenu::item:selected {{
                background-color: {theme['selection']};
            }}
            
            /* Status Bar */
            QStatusBar {{
                background-color: {theme['card']};
                color: {theme['text_secondary']};
                border-top: 1px solid {theme['border']};
                padding: 5px;
                font-size: 12px;
            }}
            
            /* Scroll Bar */
            QScrollBar:vertical {{
                background-color: {theme['card']};
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {theme['border']};
                min-height: 30px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['primary']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {theme['card']};
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {theme['border']};
                min-width: 30px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {theme['primary']};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            /* Tooltip */
            QToolTip {{
                background-color: {theme['card']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }}
        """
        
        return stylesheet