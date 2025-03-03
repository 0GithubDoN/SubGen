#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubGen - AI Subtitle Generator
Whisper transcription thread and translation services
"""

import time
import threading
from datetime import timedelta
import concurrent.futures
import requests

import torch
import whisper
from PyQt5.QtCore import QThread, pyqtSignal


class TranslationService:
    """Translation service using LibreTranslate API"""
    
    # List of LibreTranslate public instances
    SERVERS = [
        "https://translate.argosopentech.com",
        "https://libretranslate.de",
        "https://translate.terraprint.co",
        "https://lt.vern.cc"
    ]
    
    # Timeout for translation requests (seconds)
    TIMEOUT = 10
    
    @staticmethod
    def translate_text(text, target_language):
        """
        Translate text to target language using LibreTranslate
        
        Uses multiple servers with fallback and proper error handling
        """
        if not text.strip():
            return text
            
        # Define payload
        payload = {
            "q": text,
            "source": "auto",
            "target": target_language,
            "format": "text"
        }
        
        # Try each server with a timeout
        for server in TranslationService.SERVERS:
            try:
                response = requests.post(
                    f"{server}/translate", 
                    json=payload,
                    timeout=TranslationService.TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "translatedText" in result:
                        return result["translatedText"]
            except requests.RequestException:
                # Just try the next server
                continue
        
        # If all servers fail, return original text
        return text
    
    @staticmethod
    def translate_batch(texts, target_language, max_workers=4):
        """
        Translate a batch of texts in parallel
        
        Args:
            texts (list): List of text strings to translate
            target_language (str): Target language code
            max_workers (int): Maximum number of concurrent workers
            
        Returns:
            list: List of translated texts
        """
        # Filter out empty texts
        texts_to_translate = [(i, text) for i, text in enumerate(texts) if text.strip()]
        
        # If no valid texts, return original list
        if not texts_to_translate:
            return texts
            
        # Create a copy of the original list for results
        results = texts.copy()
        
        # Use ThreadPoolExecutor for parallel translation
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit translation tasks
            future_to_index = {
                executor.submit(
                    TranslationService.translate_text, 
                    text, 
                    target_language
                ): i for i, text in texts_to_translate
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    translated_text = future.result()
                    results[index] = translated_text
                except Exception:
                    # If translation fails, keep original text
                    pass
        
        return results


class WhisperTranscriptionThread(QThread):
    """Thread for running Whisper transcription without blocking the UI"""
    
    progress_update = pyqtSignal(int, str)
    transcription_complete = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, audio_path, source_language, translate=False, target_language=None, parent=None):
        super().__init__(parent)
        
        self.audio_path = audio_path
        self.source_language = source_language
        self.translate = translate
        self.target_language = target_language
        
        self.model = None
        self.cancelled = False
        
        # For time estimation
        self.start_time = None
    
    def run(self):
        """Run the transcription process"""
        try:
            self.start_time = time.time()
            
            # Load the Whisper model
            self.progress_update.emit(5, "Initializing transcription model...")
            
            # Select appropriate model size based on available GPU memory
            model_size = self._select_model_size()
            self.progress_update.emit(10, f"Loading {model_size} model...")
            
            # Load model
            self.model = whisper.load_model(model_size)
            
            # Check if operation was cancelled
            if self.cancelled:
                return
                
            self.progress_update.emit(30, "Model loaded. Starting transcription...")
            
            # Set up transcription options
            transcription_options = {}
            
            # Set the source language if specified (not auto)
            if self.source_language != "auto":
                transcription_options["language"] = self.source_language
                self.progress_update.emit(35, f"Transcribing with language: {self.source_language}")
            else:
                self.progress_update.emit(35, "Detecting language automatically...")
            
            # Transcribe the audio
            result = self.model.transcribe(
                self.audio_path, 
                **transcription_options,
                verbose=False
            )
            
            # Check if operation was cancelled
            if self.cancelled:
                return
                
            self.progress_update.emit(60, "Transcription complete. Processing results...")
            
            # Get detected language
            detected_language = result.get("language", "unknown")
            self.progress_update.emit(65, f"Detected language: {detected_language}")
            
            # Process segments
            segments = self._process_segments(result["segments"])
            
            # Check if operation was cancelled
            if self.cancelled:
                return
                
            # Handle translation if enabled
            if self.translate and self.target_language:
                segments = self._translate_segments(segments)
                
                # Check if operation was cancelled
                if self.cancelled:
                    return
            
            self.progress_update.emit(100, "Complete!")
            self.transcription_complete.emit(segments)
            
        except Exception as e:
            self.error_occurred.emit(f"Transcription error: {str(e)}")
    
    def _select_model_size(self):
        """Select appropriate Whisper model size based on available hardware"""
        model_size = "base"
        
        # Check if GPU is available
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # in GB
            
            # Choose model size based on available GPU memory
            if gpu_memory > 10:
                model_size = "large"
            elif gpu_memory > 5:
                model_size = "medium"
            elif gpu_memory > 2:
                model_size = "small"
                
            self.progress_update.emit(
                15, 
                f"Using {model_size} model with GPU acceleration ({gpu_memory:.1f} GB VRAM)"
            )
        else:
            self.progress_update.emit(15, f"Using {model_size} model (CPU mode - slower)")
        
        return model_size
    
    def _process_segments(self, raw_segments):
        """Process the raw Whisper segments into a standardized format"""
        segments = []
        total_segments = len(raw_segments)
        
        for idx, segment in enumerate(raw_segments):
            # Check if operation was cancelled
            if self.cancelled:
                return []
                
            # Format the timing information
            start_time = str(timedelta(seconds=segment["start"])).rjust(12, "0")[:-3].replace(".", ",")
            end_time = str(timedelta(seconds=segment["end"])).rjust(12, "0")[:-3].replace(".", ",")
            
            # Clean up the text
            text = segment["text"].strip()
            
            # Add to segments
            segments.append({
                "start": start_time,
                "end": end_time,
                "text": text
            })
            
            # Update progress (from 65 to 85 if not translating)
            if not self.translate:
                progress = 65 + int((idx + 1) / total_segments * 30)
                self.progress_update.emit(
                    progress, 
                    f"Processing segment {idx+1}/{total_segments}"
                )
        
        return segments
    
    def _translate_segments(self, segments):
        """Translate all segments using the translation service"""
        self.progress_update.emit(70, "Starting translation...")
        
        # Extract all texts
        texts = [segment["text"] for segment in segments]
        total_texts = len(texts)
        
        # Translate in smaller batches for better progress tracking
        batch_size = max(5, total_texts // 10)  # Aim for around 10 batches
        translated_segments = segments.copy()
        
        for i in range(0, total_texts, batch_size):
            # Check if operation was cancelled
            if self.cancelled:
                return []
                
            # Get the current batch
            batch = texts[i:i+batch_size]
            batch_indices = list(range(i, min(i+batch_size, total_texts)))
            
            # Update progress
            progress = 70 + int(i / total_texts * 25)
            self.progress_update.emit(
                progress, 
                f"Translating segments {i+1}-{i+len(batch)}/{total_texts}"
            )
            
            # Translate batch
            translated_batch = TranslationService.translate_batch(
                batch, 
                self.target_language
            )
            
            # Update segments with translations
            for j, idx in enumerate(batch_indices):
                translated_segments[idx]["text"] = translated_batch[j]
        
        self.progress_update.emit(95, "Translation completed.")
        return translated_segments
    
    def cancel(self):
        """Cancel the ongoing transcription"""
        self.cancelled = True
        self.progress_update.emit(0, "Cancelling operation...")