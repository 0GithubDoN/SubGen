from setuptools import setup, find_packages

setup(
    name="subgen",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "openai-whisper",
        "PyQt5",
        "requests",
        "ffmpeg-python",
    ],
    py_modules=[
        "main",
        "theme",
        "components",
        "transcription",
        "utils",
    ],
    entry_points={
        "console_scripts": [
            "subgen=main:main",
        ],
    },
    author="SubGen",
    author_email="",
    description="AI-powered subtitle generator using OpenAI Whisper",
    keywords="subtitle, AI, Whisper, transcription, translation",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Multimedia :: Video",
    ],
)