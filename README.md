## ⚠️ Disclaimer

This tool is for **educational purposes only**. You are responsible for complying with YouTube's Terms of Service and copyright laws. Only download content you own or have permission to use.

#🎬 YouTube Downloader

A clean, modern YouTube downloader with both GUI and CLI interfaces. Built by a 15-year-old developer learning Python.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Features

- 🎨 **Modern GUI** - Clean dark theme with real-time progress
- 🎬 **Video Download** - MP4 in multiple qualities (360p to 1080p) (wip, 360p is only working for now)
- 🎵 **Audio Extraction** - MP3 format (works without FFmpeg!)
- 🔍 **Smart Quality Check** - See available formats before downloading
- 📋 **One-Click Paste** - Auto-paste from clipboard

## 📋 Requirements
- Python 3.8+
- yt-dlp (auto-installs if missing)
- FFmpeg (optional, for 1080p+ video)

## 🛠️ Tech Stack
Python • tkinter • yt-dlp • threading



## 🚀 Quick Start

```bash
# Install
pip install yt-dlp

# Run GUI
python youtube_downloader.py

# Or CLI
python youtube_downloader.py "https://youtube.com/watch?v=..."


