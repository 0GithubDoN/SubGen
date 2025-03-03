#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubGen - AI Subtitle Generator
Custom UI components
"""

import time
import math  # Moved import to the top
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtSignal, pyqtProperty, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QFont
from PyQt5.QtWidgets import (
    QLabel, QTextEdit, QScrollArea, QVBoxLayout, QHBoxLayout, 
    QWidget, QFrame, QPushButton, QSizePolicy, QProgressBar,
    QSpacerItem
)


class CustomProgressBar(QProgressBar):
    """Custom progress bar with smooth animation and gradient fill"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize values first
        self._animation_value = 0
        self._target_value = 0
        
        # Animation properties
        self._animation = QPropertyAnimation(self, b"animationValue")
        self._animation.setDuration(600)  # Animation duration in milliseconds
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Set minimum height
        self.setMinimumHeight(16)
        
        # Set text format
        self.setFormat("%p%")
        
        # Enable custom drawing
        self.setTextVisible(True)
    
    @pyqtProperty(float)
    def animationValue(self):
        return self._animation_value
    
    @animationValue.setter
    def animationValue(self, value):
        self._animation_value = value
        super().setValue(int(value))
        self.update()  # Force update of the widget
    
    def setValue(self, value):
        """Set value with animation"""
        # Save the target value
        self._target_value = value
        
        # Stop any running animation
        if self._animation.state() == QPropertyAnimation.Running:
            self._animation.stop()
        
        # Set up and start the animation
        self._animation.setStartValue(self._animation_value)
        self._animation.setEndValue(value)
        self._animation.start()
    
    def paintEvent(self, event):
        """Custom paint event for prettier progress bar"""
        # Call the base class implementation to get the standard look
        super().paintEvent(event)


class DropArea(QLabel):
    """Custom label for drag and drop functionality with animation effects"""
    
    file_dropped = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(120)
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        self.setProperty("class", "drop-area")
        self.setText("🎬 Drag & Drop Video or Audio File Here\n\nor click Browse Files below")
        
        # Track drag enter state
        self.dragEntered = False
        
        # Initialize property values first
        self.pulseValue = 0.0
        self.shimmerValue = -1.0
        
        # Create animations after the values are initialized
        # Pulsing animation
        self.pulseAnimation = QPropertyAnimation(self, b"pulse")
        self.pulseAnimation.setDuration(1500)
        self.pulseAnimation.setStartValue(0.0)
        self.pulseAnimation.setEndValue(1.0)
        self.pulseAnimation.setLoopCount(-1)  # Infinite loop
        self.pulseAnimation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Shimmer animation
        self.shimmerAnimation = QPropertyAnimation(self, b"shimmer")
        self.shimmerAnimation.setDuration(2000)
        self.shimmerAnimation.setStartValue(-1.0)  # Start from left of widget
        self.shimmerAnimation.setEndValue(1.0)     # End at right of widget
        self.shimmerAnimation.setLoopCount(-1)     # Infinite loop
        
        # Start pulsing animation
        self.pulseAnimation.start()
    
    @pyqtProperty(float)
    def pulse(self):
        return self.pulseValue
    
    @pulse.setter
    def pulse(self, value):
        self.pulseValue = value
        self.update()
    
    @pyqtProperty(float)
    def shimmer(self):
        return self.shimmerValue
    
    @shimmer.setter
    def shimmer(self, value):
        self.shimmerValue = value
        self.update()
    
    def dragEnterEvent(self, event):
        """Handle file drag enter"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.dragEntered = True
            
            # Stop pulse animation
            self.pulseAnimation.stop()
            
            # Start shimmer animation
            self.shimmerAnimation.start()
            
            self.update()
    
    def dragLeaveEvent(self, event):
        """Handle file drag leave"""
        self.dragEntered = False
        
        # Stop shimmer animation
        self.shimmerAnimation.stop()
        
        # Restart pulse animation
        self.pulseAnimation.start()
        
        self.update()
    
    def dropEvent(self, event):
        """Handle file drop"""
        self.dragEntered = False
        
        # Stop animations
        self.shimmerAnimation.stop()
        self.pulseAnimation.start()
        
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.file_dropped.emit(file_path)
    
    def paintEvent(self, event):
        """Custom paint event for visual effects"""
        # Get colors from theme based on widget state
        if self.dragEntered:
            # Highlighted state during drag
            borderColor = self.palette().highlight().color()
            bgColor = QColor(borderColor)
            bgColor.setAlpha(40)  # Semi-transparent background
        else:
            # Normal state with subtle pulsing
            borderColor = self.palette().mid().color()
            
            # Create pulsing effect
            pulseIntensity = 0.5 + 0.5 * abs(math.sin(self.pulseValue * math.pi))
            bgColor = QColor(self.palette().window().color())
            
            # Slightly modify the background based on pulse
            if self.palette().window().color().lightness() > 128:
                # Light theme - darken slightly
                bgColor = bgColor.darker(int(100 + 5 * pulseIntensity))
            else:
                # Dark theme - lighten slightly
                bgColor = bgColor.lighter(int(100 + 10 * pulseIntensity))
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw rounded rectangle background
        pen = QPen(borderColor)
        pen.setStyle(Qt.DashLine)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(bgColor)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)
        
        # Draw shimmer effect during drag
        if self.dragEntered:
            # Create a diagonal shimmer highlight
            shimmerPos = self.shimmerValue
            gradient = QtGui.QLinearGradient(
                shimmerPos * self.width(), 0,
                shimmerPos * self.width() + 50, self.height()
            )
            gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
            gradient.setColorAt(0.5, QColor(255, 255, 255, 50))
            gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)
        
        # Draw the text
        painter.setPen(self.palette().text().color())
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())


class SegmentItem(QFrame):
    """Individual subtitle segment display with editing capability"""
    
    text_changed = pyqtSignal(int, str)
    
    def __init__(self, segment_id, start_time, end_time, text, parent=None):
        super().__init__(parent)
        
        self.segment_id = segment_id
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setProperty("class", "segment-item")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI for this segment"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Header with index and time information
        header_layout = QHBoxLayout()
        
        # Segment index label
        index_label = QLabel(f"#{self.segment_id}")
        index_label.setProperty("class", "segment-index")
        header_layout.addWidget(index_label)
        
        # Time range
        time_label = QLabel(f"{self.start_time} → {self.end_time}")
        time_label.setProperty("class", "segment-time")
        header_layout.addWidget(time_label)
        
        header_layout.addStretch()
        
        # Duration calculation
        try:
            start_parts = self.start_time.split(':')
            end_parts = self.end_time.split(':')
            
            start_seconds = int(start_parts[0]) * 3600 + int(start_parts[1]) * 60 + float(start_parts[2].replace(',', '.'))
            end_seconds = int(end_parts[0]) * 3600 + int(end_parts[1]) * 60 + float(end_parts[2].replace(',', '.'))
            
            duration = end_seconds - start_seconds
            duration_label = QLabel(f"{duration:.1f}s")
            duration_label.setProperty("class", "segment-duration")
            header_layout.addWidget(duration_label)
        except:
            # In case of parsing error, just ignore duration
            pass
        
        layout.addLayout(header_layout)
        
        # Text editor for the subtitle
        self.text_edit = QTextEdit(self.text)
        self.text_edit.setProperty("class", "segment-text")
        self.text_edit.setTabChangesFocus(True)
        self.text_edit.setMinimumHeight(60)
        self.text_edit.setMaximumHeight(100)
        self.text_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_edit)
    
    def on_text_changed(self):
        """Handle text changes"""
        self.text = self.text_edit.toPlainText()
        self.text_changed.emit(self.segment_id, self.text)
    
    def get_data(self):
        """Get the current segment data"""
        return {
            'id': self.segment_id,
            'start': self.start_time,
            'end': self.end_time,
            'text': self.text_edit.toPlainText()
        }


class SubtitleEditor(QScrollArea):
    """Scrollable editor for subtitle segments"""
    
    content_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        
        # Container widget for segments
        self.container = QWidget()
        self.setWidget(self.container)
        
        # Layout for segments
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        
        # Add stretch to push all content to the top
        self.layout.addStretch()
        
        # List of segment widgets
        self.segment_widgets = []
    
    def clear_segments(self):
        """Remove all segment widgets"""
        # Remove all existing segments
        for widget in self.segment_widgets:
            self.layout.removeWidget(widget)
            widget.deleteLater()
        
        self.segment_widgets = []
    
    def set_segments(self, segments):
        """Set new segments to display"""
        # Clear existing segments
        self.clear_segments()
        
        # Add new segments
        for idx, segment in enumerate(segments, 1):
            segment_widget = SegmentItem(
                idx,
                segment['start'],
                segment['end'],
                segment['text'],
                self
            )
            
            # Connect signal
            segment_widget.text_changed.connect(self.on_segment_changed)
            
            # Insert before the stretch item
            self.layout.insertWidget(self.layout.count() - 1, segment_widget)
            self.segment_widgets.append(segment_widget)
    
    def on_segment_changed(self, segment_id, text):
        """Handle segment text changes"""
        self.content_changed.emit()
    
    def get_segments(self):
        """Get current segments with any edits"""
        segments = []
        for widget in self.segment_widgets:
            data = widget.get_data()
            segments.append({
                'start': data['start'],
                'end': data['end'],
                'text': data['text']
            })
        return segments
    
    def get_srt_content(self):
        """Get segments formatted as SRT content"""
        srt_content = ""
        segments = self.get_segments()
        
        for idx, segment in enumerate(segments, 1):
            srt_content += f"{idx}\n{segment['start']} --> {segment['end']}\n{segment['text']}\n\n"
            
        return srt_content