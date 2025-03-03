# SubGen - AI Subtitle Generator

A powerful, easy-to-use AI-powered subtitle generator for personal use. This tool allows you to automatically generate subtitles for video and audio files using OpenAI's Whisper model, with a focus on user experience and design.

## Features

- ✅ **Modern & Enhanced UI**
  - Beautiful, modern interface with Material Design icons
  - **NEW**: Light and dark theme support with automatic system detection
  - **NEW**: Responsive design that adapts to any window size
  - Intuitive drag & drop functionality with visual feedback
  - **NEW**: Improved progress tracking with time estimation
  - **NEW**: Segment-based subtitle editor for precise editing

- ✅ **AI-Powered Transcription & Translation**
  - Uses OpenAI Whisper for high-accuracy transcription
  - Multiple language support (including Romanian, English, Spanish, and more)
  - **NEW**: Enhanced translation with parallel processing and better server fallback
  - **NEW**: Improved error handling for translation services
  - Built-in translation using LibreTranslate
  - SRT and VTT export formats

- ✅ **Versatile File Support**
  - Video: MKV, MP4, AVI, MOV, WEBM, FLV
  - Audio: MP3, WAV, AAC, FLAC, OGG, EAC3
  - Automatic format detection and processing

- ✅ **Advanced Features**
  - Automatic audio extraction from video
  - One-click subtitle generation with cancellation support
  - **NEW**: Intelligent dependency management - installs packages only when needed
  - **NEW**: Update option to refresh dependencies when needed
  - Options for soft subtitles (external files) or hardcoded subtitles
  - Enhanced error handling and user feedback
  - **NEW**: Automatic resource management

## Installation

### Prerequisites
- Python 3.8+ (Python 3.10 or 3.11 recommended)
- FFmpeg (for audio extraction and subtitle embedding)

### Windows Installation
1. Make sure Python and FFmpeg are installed and added to your PATH
2. Run the `install.bat` script
3. Wait for the installation to complete
4. Navigate to the created SubGen folder
5. Run `SubGen.bat` to start the application

### Mac/Linux Installation
1. Make sure Python and FFmpeg are installed
2. Make the install script executable: `chmod +x install.sh`
3. Run the script: `./install.sh`
4. Wait for the installation to complete
5. Launch the application using `./SubGen.sh` or the desktop shortcut

### Updating Dependencies
To check for and install updates to dependencies:
- Windows: Run `SubGen.bat --update`
- Mac/Linux: Run `./SubGen.sh --update`

### Troubleshooting Whisper Installation
If you encounter an error installing Whisper during setup, manually install it with:

```
cd SubGen
venv\Scripts\activate    # On Windows
source venv/bin/activate # On Mac/Linux

# Try this first:
pip install git+https://github.com/openai/whisper.git

# If that doesn't work, try:
pip install --upgrade setuptools wheel
pip install openai-whisper
```

## How to Use

1. **Open the application** by running SubGen.bat (Windows) or SubGen.sh (Mac/Linux)
2. **Select a file** by clicking "Browse Files" or dragging and dropping a video/audio file
3. **Choose language settings**:
   - Select source language for transcription
   - Optionally enable translation and select target language
4. **Click "Generate Subtitles"** and wait for the transcription to complete
   - You can monitor progress and estimated completion time
   - Cancel the process at any time if needed
5. **Preview and edit** the subtitles in the segment-based editor:
   - Each subtitle segment can be individually edited
   - Duration and timing information is displayed for each segment
6. **Save or embed the subtitles**:
   - Save as .SRT or .VTT file
   - Embed directly into video (soft or hard subtitles)
7. **Toggle Dark Mode** using the theme button in the top-right corner

## Advanced Options

- **Translation Service**: Uses LibreTranslate for free, open-source translation with robust server fallback
- **Subtitle Embedding**: Choose between soft subtitles (can be turned on/off) or hardcoded subtitles (permanently visible)
- **GPU Acceleration**: The application automatically detects and uses GPU acceleration for faster transcription if available
- **Dependency Management**: Smart dependency checking that only installs what's needed and offers updates when available
- **Theme Settings**: Toggle between light and dark modes to match your preference

## System Requirements

- **OS**: Windows 10/11, macOS 10.13+, or Linux
- **RAM**: 4GB minimum, 8GB+ recommended
- **Storage**: 5GB free space for the application and models
- **GPU**: Optional, but recommended for faster processing (NVIDIA GPU with CUDA support)
<img src="https://i.ibb.co/zTRw5jNt/1.png" alt="1" border="0">
## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- **OpenAI Whisper**: For the AI transcription model
- **LibreTranslate**: For open-source translation capabilities
- **FFmpeg**: For media processing capabilities
- **PyQt5**: For the user interface components
- **Material Design Icons**: For the modern UI elements

## Support

For issues and feature requests, please create an issue on the GitHub repository or contact the developer directly.

## Recent Updates

- **NEW** (v1.1.0): Added light/dark theme toggle
- **NEW** (v1.1.0): Enhanced subtitle editor with segmented interface
- **NEW** (v1.1.0): Improved translation with parallel processing
- **NEW** (v1.1.0): Added Romanian language support
- **NEW** (v1.1.0): Intelligent dependency management
- **NEW** (v1.1.0): Responsive design for all window sizes
- **NEW** (v1.1.0): Progress time estimation and cancellation
- **NEW** (v1.1.0): Reorganized code structure for better maintainability
- Added modern UI with Material Design icons
- Integrated LibreTranslate for translation support
- Improved file handling with direct paths
- Enhanced drag & drop interface with visual feedback
