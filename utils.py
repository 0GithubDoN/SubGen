#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubGen - AI Subtitle Generator
Utility functions
"""

import os
import math
from pathlib import Path


def format_time(seconds):
    """
    Format seconds as a human-readable time string.
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def format_file_size(size_bytes):
    """
    Format a file size in bytes as a human-readable string.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted file size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        kb = size_bytes / 1024
        return f"{kb:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        mb = size_bytes / (1024 * 1024)
        return f"{mb:.1f} MB"
    else:
        gb = size_bytes / (1024 * 1024 * 1024)
        return f"{gb:.2f} GB"


def ensure_directory(directory_path):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path (str or Path): Directory path
        
    Returns:
        Path: Path object for the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_srt_to_vtt(srt_content):
    """
    Convert SRT content to VTT format.
    
    Args:
        srt_content (str): Content in SRT format
        
    Returns:
        str: Content in VTT format
    """
    # Start with the VTT header
    vtt_content = "WEBVTT\n\n"
    
    # Split by double newline to get each subtitle block
    srt_blocks = srt_content.split("\n\n")
    for block in srt_blocks:
        if not block.strip():
            continue
            
        lines = block.split("\n")
        if len(lines) >= 3:
            # Skip the subtitle number (first line)
            
            # Convert timestamp format
            # SRT: 00:00:20,000 --> 00:00:22,500
            # VTT: 00:00:20.000 --> 00:00:22.500
            timestamp = lines[1].replace(",", ".")
            
            # Add the text
            text = "\n".join(lines[2:])
            
            vtt_content += f"{timestamp}\n{text}\n\n"
    
    return vtt_content


def get_file_duration(file_path):
    """
    Get the duration of a media file using FFmpeg.
    
    Args:
        file_path (str): Path to media file
        
    Returns:
        float: Duration in seconds or None if unavailable
    """
    try:
        import subprocess
        import json
        
        # Run FFprobe to get duration
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            file_path
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = float(data["format"]["duration"])
            return duration
        
        return None
    except:
        return None


def calculate_reading_speed(subtitle_segments, total_duration=None):
    """
    Calculate the average reading speed (characters per second) for subtitle segments.
    
    Args:
        subtitle_segments (list): List of subtitle segment dictionaries
        total_duration (float, optional): Total duration in seconds (if known)
        
    Returns:
        dict: Statistics including average speed, total characters, etc.
    """
    if not subtitle_segments:
        return {
            "avg_speed": 0,
            "total_chars": 0,
            "total_words": 0,
            "total_duration": 0
        }
    
    total_chars = 0
    total_words = 0
    segment_durations = []
    
    for segment in subtitle_segments:
        # Get text
        text = segment["text"]
        total_chars += len(text)
        total_words += len(text.split())
        
        # Calculate segment duration
        try:
            # Parse start and end times
            start_parts = segment["start"].split(":")
            end_parts = segment["end"].split(":")
            
            start_seconds = (
                int(start_parts[0]) * 3600 + 
                int(start_parts[1]) * 60 + 
                float(start_parts[2].replace(",", "."))
            )
            
            end_seconds = (
                int(end_parts[0]) * 3600 + 
                int(end_parts[1]) * 60 + 
                float(end_parts[2].replace(",", "."))
            )
            
            duration = end_seconds - start_seconds
            segment_durations.append(duration)
        except:
            pass
    
    # Calculate total speaking duration from segments
    total_speaking_duration = sum(segment_durations)
    
    # Calculate reading speeds
    avg_speed_cps = total_chars / total_speaking_duration if total_speaking_duration > 0 else 0
    avg_speed_wpm = (total_words / total_speaking_duration) * 60 if total_speaking_duration > 0 else 0
    
    return {
        "avg_speed_cps": avg_speed_cps,
        "avg_speed_wpm": avg_speed_wpm,
        "total_chars": total_chars,
        "total_words": total_words,
        "total_speaking_duration": total_speaking_duration,
        "total_duration": total_duration or total_speaking_duration
    }


def validate_timestamp(timestamp_str):
    """
    Validate and normalize an SRT timestamp string.
    
    Args:
        timestamp_str (str): The timestamp string to validate
        
    Returns:
        str: Normalized timestamp string or None if invalid
    """
    try:
        # Check format
        parts = timestamp_str.split(":")
        if len(parts) != 3:
            return None
            
        hours = int(parts[0])
        minutes = int(parts[1])
        
        # Handle seconds with milliseconds
        seconds_parts = parts[2].replace(",", ".").split(".")
        seconds = int(seconds_parts[0])
        
        # Validate ranges
        if not (0 <= hours and 0 <= minutes < 60 and 0 <= seconds < 60):
            return None
            
        # Normalize format
        if "," in parts[2]:
            milliseconds = parts[2].split(",")[1].ljust(3, "0")[:3]
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds}"
        else:
            milliseconds = parts[2].split(".")[1].ljust(3, "0")[:3] if "." in parts[2] else "000"
            return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds}"
            
    except ValueError:
        return None
    
    
def get_subtitle_stats(segments):
    """
    Get statistics about subtitle segments.
    
    Args:
        segments (list): List of subtitle segment dictionaries
        
    Returns:
        dict: Statistics including count, duration, etc.
    """
    if not segments:
        return {
            "count": 0,
            "duration": 0,
            "avg_length": 0,
            "max_length": 0
        }
    
    # Count segments
    count = len(segments)
    
    # Character statistics
    char_lengths = [len(s["text"]) for s in segments]
    avg_length = sum(char_lengths) / count if count > 0 else 0
    max_length = max(char_lengths) if char_lengths else 0
    
    # Duration calculation
    durations = []
    for segment in segments:
        try:
            start_parts = segment["start"].split(":")
            end_parts = segment["end"].split(":")
            
            start_seconds = (
                int(start_parts[0]) * 3600 + 
                int(start_parts[1]) * 60 + 
                float(start_parts[2].replace(",", "."))
            )
            
            end_seconds = (
                int(end_parts[0]) * 3600 + 
                int(end_parts[1]) * 60 + 
                float(end_parts[2].replace(",", "."))
            )
            
            durations.append(end_seconds - start_seconds)
        except:
            pass
    
    avg_duration = sum(durations) / len(durations) if durations else 0
    total_duration = sum(durations) if durations else 0
    
    return {
        "count": count,
        "total_duration": total_duration,
        "avg_duration": avg_duration,
        "avg_length": avg_length,
        "max_length": max_length
    }