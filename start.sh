#!/bin/bash

echo "Starting SubGen - AI Subtitle Generator..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if requirements are installed
if [ ! -d "venv/lib/python3.*/site-packages/PyQt5" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Check if icons are downloaded
if [ ! -d "icons" ]; then
    echo "Downloading icons..."
    python download_icons.py
fi

# Check if resource file is compiled
if [ ! -f "resources_rc.py" ]; then
    echo "Compiling resources..."
    pyrcc5 resources.qrc -o resources_rc.py
fi

# Start the application
python main.py