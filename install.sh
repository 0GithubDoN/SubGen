#!/bin/bash
# SubGen Installer Script - Easy installation for AI Subtitle Generator
# This script installs all dependencies and sets up the application

echo "======================================================"
echo "  SubGen - AI Subtitle Generator Installer"
echo "======================================================"
echo

echo "Checking dependencies..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python not found. Please install Python 3.8 or higher"
    echo "After installation, run this script again"
    exit 1
fi

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg not found. Please install FFmpeg using your package manager"
    echo "For example:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "After installation, run this script again"
    exit 1
fi

# Create directory and virtual environment
echo "Creating Python virtual environment..."
mkdir -p SubGen
cd SubGen
python3 -m venv venv
source venv/bin/activate

# Install required packages
echo "Installing required Python packages..."
echo
echo "Step 1: Upgrading pip, setuptools and wheel..."
python -m pip install --upgrade pip setuptools wheel
echo

echo "Step 2: Installing PyTorch..."
pip install torch torchvision torchaudio
echo

echo "Step 3: Installing Whisper from GitHub..."
pip install git+https://github.com/openai/whisper.git
echo

echo "Step 4: Installing FFmpeg dependency..."
pip install ffmpeg-python
echo

echo "Step 5: Installing PyQt5..."
pip install PyQt5
echo

echo "Step 6: Installing requests for translation support..."
pip install requests
echo

# Copy files
echo "Setting up application files..."
# Copy the new multi-file structure
for pyfile in ../main.py ../theme.py ../components.py ../transcription.py ../utils.py; do
    if [ -f "$pyfile" ]; then
        cp "$pyfile" .
        echo "Copied $(basename "$pyfile")"
    else
        echo "Warning: Required file $pyfile not found!"
    fi
done

# Copy setup files
cp ../setup.py . 2>/dev/null
cp ../download_icons.py . 2>/dev/null
cp ../resources.qrc . 2>/dev/null

# Download icons
echo "Downloading required icons..."
python download_icons.py

# Check if resource file is compiled
if command -v pyrcc5 &> /dev/null; then
    echo "Compiling resources..."
    pyrcc5 resources.qrc -o resources_rc.py
else
    echo "Warning: pyrcc5 not found. Resources will not be compiled."
    echo "You can manually compile resources with: pyrcc5 resources.qrc -o resources_rc.py"
fi

# Create requirements file
cat > requirements.txt << 'EOL'
torch>=2.0.0
openai-whisper>=1.0.0
ffmpeg-python>=0.2.0
PyQt5>=5.15.0
requests>=2.28.0
EOL

# Create launcher script
echo "Creating launcher script..."
cat > SubGen.sh << 'EOL'
#!/bin/bash
# SubGen Launcher Script
# Usage:
#   ./SubGen.sh         - Run the application
#   ./SubGen.sh --update - Run and update dependencies first

cd "$(dirname "$0")"
source venv/bin/activate

echo "Starting SubGen - AI Subtitle Generator..."

# Check and install required dependencies
echo "Checking dependencies..."

# Check if requirements file exists
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << EOF
torch>=2.0.0
openai-whisper>=1.0.0
ffmpeg-python>=0.2.0
PyQt5>=5.15.0
requests>=2.28.0
EOF
fi

# Use pip to check which packages need to be installed/updated
missing_packages=$(python -m pip list --outdated --format=freeze | cut -d = -f 1)
needed_packages=$(grep -v "^\s*#" requirements.txt | cut -d = -f 1 | xargs pip list --format=freeze | cut -d = -f 1)

# Find packages that are in requirements.txt but not installed
for package in $(grep -v "^\s*#" requirements.txt | cut -d = -f 1); do
    if ! echo "$needed_packages" | grep -q "^$package$"; then
        echo "Installing missing package: $package"
        pip install "$package"
    fi
done

# Check for updates only when --update flag is provided
if [[ "$1" == "--update" ]]; then
    echo "Checking for package updates..."
    for package in $missing_packages; do
        echo "Updating $package..."
        pip install --upgrade "$package"
    done
fi

# Check if icons are downloaded
if [ ! -d "icons" ]; then
    echo "Downloading icons..."
    python download_icons.py
fi

# Check if resource file is compiled
if [ ! -f "resources_rc.py" ] && command -v pyrcc5 &> /dev/null; then
    echo "Compiling resources..."
    pyrcc5 resources.qrc -o resources_rc.py
fi

# Check for required Python files
missing_files=false
for file in main.py theme.py components.py transcription.py utils.py; do
    if [ ! -f "$file" ]; then
        echo "Error: Required file $file is missing!"
        missing_files=true
    fi
done

if [ "$missing_files" = true ]; then
    echo "Please make sure all required files are in the current directory."
    exit 1
fi

# Start the application
python main.py
EOL

chmod +x SubGen.sh

# Create desktop shortcut
echo "Creating desktop shortcut..."
cat > ~/Desktop/SubGen.desktop << EOL
[Desktop Entry]
Name=SubGen
Comment=AI Subtitle Generator
Exec=$(pwd)/SubGen.sh
Icon=$(pwd)/icons/app_icon.png
Terminal=false
Type=Application
Categories=Utility;AudioVideo;
EOL

chmod +x ~/Desktop/SubGen.desktop

echo "======================================================"
echo "  Installation Complete!"
echo "======================================================"
echo
echo "You can now run SubGen by:"
echo "1. Open the 'SubGen' folder"
echo "2. Run './SubGen.sh'"
echo "Or use the desktop shortcut that was created"
echo
echo "The application includes:"
echo "- Modern UI with light/dark theme support"
echo "- Speech-to-text transcription"
echo "- Translation to multiple languages (including Romanian)"
echo "- Support for various audio and video formats"
echo "- Options to save as SRT, VTT, or embed directly into videos"
echo "- Improved segment editor for precise subtitle editing"
echo
echo "Enjoy generating subtitles with AI!"