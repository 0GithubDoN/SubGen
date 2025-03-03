@echo off
echo ======================================================
echo   SubGen - AI Subtitle Generator Installer
echo ======================================================
echo.

echo Checking dependencies...

:: Check for Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Please install Python from https://www.python.org/downloads/
    echo Make sure to check 'Add Python to PATH' during installation
    echo After installation, run this script again
    pause
    exit /b 1
)

:: Check for FFmpeg
ffmpeg -version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo FFmpeg not found. Please install FFmpeg from https://ffmpeg.org/download.html
    echo Make sure to add FFmpeg to your PATH environment variable
    echo After installation, run this script again
    pause
    exit /b 1
)

:: Create directory and virtual environment
echo Creating Python virtual environment...
mkdir SubGen 2>nul
cd SubGen
python -m venv venv
call venv\Scripts\activate.bat

:: Install required packages
echo Installing required Python packages...
echo.
echo Step 1: Upgrading pip, setuptools and wheel...
python -m pip install --upgrade pip setuptools wheel
echo.

echo Step 2: Installing PyTorch...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
echo.

echo Step 3: Installing Whisper from GitHub...
pip install git+https://github.com/openai/whisper.git
echo.

echo Step 4: Installing FFmpeg dependency...
pip install ffmpeg-python
echo.

echo Step 5: Installing PyQt5 and tools...
pip install PyQt5
echo.

echo Step 6: Installing requests for translation support...
pip install requests
echo.

:: Copy files
echo Setting up application files...
:: Copy the new multi-file structure
for %%F in (..\main.py ..\theme.py ..\components.py ..\transcription.py ..\utils.py) do (
    if exist %%F (
        copy %%F .
        echo Copied %%~nxF
    ) else (
        echo Warning: Required file %%F not found!
    )
)

:: Copy setup files
copy ..\setup.py . 2>nul
copy ..\download_icons.py . 2>nul
copy ..\resources.qrc . 2>nul

:: Download icons
echo Downloading required icons...
python download_icons.py

:: Check for PyQt5 tools and compile resources
where pyrcc5 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Compiling resources...
    pyrcc5 resources.qrc -o resources_rc.py
) else (
    echo Warning: pyrcc5 not found. Resources will not be compiled.
    echo You can manually compile resources with: pyrcc5 resources.qrc -o resources_rc.py
)

:: Create requirements file (fixed version)
(
echo torch>=2.0.0
echo openai-whisper>=1.0.0
echo ffmpeg-python>=0.2.0
echo PyQt5>=5.15.0
echo requests>=2.28.0
) > requirements.txt

:: Create launcher
echo Creating launcher script...
(
echo @echo off
echo :: SubGen Launcher Script
echo :: Usage:
echo ::   SubGen.bat         - Run the application
echo ::   SubGen.bat --update - Run and update dependencies first
echo.
echo cd %%~dp0
echo call venv\Scripts\activate.bat
echo.
echo echo Starting SubGen - AI Subtitle Generator...
echo.
echo :: Check and install missing packages
echo echo Checking dependencies...
echo.
echo :: Check for the --update flag
echo set UPDATE=0
echo for %%%%i in (%%*^) do (
echo   if "%%%%i"=="--update" set UPDATE=1
echo ^)
echo.
echo :: Check for each required package
echo setlocal enabledelayedexpansion
echo for /f "tokens=1,2 delims==" %%%%i in (requirements.txt^) do (
echo   for /f "tokens=1 delims=>=" %%%%a in ("%%%%i"^) do (
echo     pip show %%%%a ^>nul 2^>^&1
echo     if !errorlevel! neq 0 (
echo       echo Installing missing package: %%%%i
echo       pip install %%%%i
echo     ^) else if !UPDATE!==1 (
echo       echo Updating package: %%%%i
echo       pip install --upgrade %%%%i
echo     ^)
echo   ^)
echo ^)
echo.
echo :: Check if icons are downloaded
echo if not exist icons\ (
echo   echo Downloading icons...
echo   python download_icons.py
echo ^)
echo.
echo :: Check if resources are compiled
echo if not exist resources_rc.py (
echo   where pyrcc5 ^>nul 2^>^&1
echo   if !errorlevel! equ 0 (
echo     echo Compiling resources...
echo     pyrcc5 resources.qrc -o resources_rc.py
echo   ^)
echo ^)
echo.
echo :: Check for required Python files
echo set MISSING=0
echo for %%%%f in (main.py theme.py components.py transcription.py utils.py^) do (
echo   if not exist %%%%f (
echo     echo Error: Required file %%%%f is missing!
echo     set MISSING=1
echo   ^)
echo ^)
echo.
echo if !MISSING!==1 (
echo   echo Please make sure all required files are in the current directory.
echo   exit /b 1
echo ^)
echo.
echo :: Start the application
echo python main.py
echo.
echo :: Pause at the end
echo pause
) > SubGen.bat

echo ======================================================
echo   Installation Complete!
echo ======================================================
echo.
echo You can now run SubGen by:
echo 1. Open the 'SubGen' folder
echo 2. Run 'SubGen.bat'
echo.
echo The application includes:
echo - Modern UI with light/dark theme support
echo - Speech-to-text transcription
echo - Translation to multiple languages (including Romanian)
echo - Support for various audio and video formats
echo - Options to save as SRT, VTT, or embed directly into videos
echo - Improved segment editor for precise subtitle editing
echo.
echo Enjoy generating subtitles with AI!
pause