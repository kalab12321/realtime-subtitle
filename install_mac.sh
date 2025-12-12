#!/bin/bash

echo "==================================================="
echo "  Real-Time Translator - macOS Installer"
echo "==================================================="

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Please install it via brew: brew install python"
    exit 1
fi

# 2. Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[1/4] Creating virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "[1/4] Virtual environment exists."
fi

# 3. Activate & Install
echo "[2/4] Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Apple Silicon Optimization
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    echo "[3/4] Apple Silicon (M1/M2/M3) detected!"
    echo "      Installing mlx-whisper for Metal GPU acceleration..."
    pip install mlx-whisper
else
    echo "[3/4] Intel Mac detected. Using standard larger models."
fi

# 5. Check System Dependencies
echo "[4/5] Checking system tools..."
MISSING_TOOLS=0

if ! command -v ffmpeg &> /dev/null; then
    echo "  [WARNING] ffmpeg is MISSING."
    echo "  -> Run: brew install ffmpeg"
    MISSING_TOOLS=1
else
    echo "  [OK] ffmpeg found."
fi

if [ $MISSING_TOOLS -eq 1 ]; then
    echo ""
    echo "Please install the missing tools above manually."
fi

# 6. Virtual Audio Device
echo "[5/5] Checking virtual audio device..."
if [ -d "/Library/Audio/Plug-Ins/HAL/BlackHole2ch.driver" ] || [ -d "/Library/Audio/Plug-Ins/HAL/BlackHole2ch.driver" ]; then
    echo "  [OK] BlackHole virtual audio device found."
else
    echo "  [WARNING] BlackHole virtual audio device is NOT installed."
    echo "  -> BlackHole is required to capture system audio (e.g., from games, meetings, videos)."
    echo "  -> Install via Homebrew: brew install blackhole-2ch"
    echo "  -> Or download from: https://existential.audio/blackhole/"
    echo ""
fi

# 7. Optional: SwitchAudioSource for programmatic device switching
if command -v SwitchAudioSource &> /dev/null; then
    echo "  [OK] SwitchAudioSource found (for device management)."
else
    echo "  [INFO] SwitchAudioSource not found (optional)."
    echo "  -> Install for better device management: brew install switchaudio-osx"
    echo "  -> This enables programmatic audio device switching in the dashboard."
    echo ""
fi

echo ""
echo "==================================================="
echo "  Installation Complete!"
echo "  Run './start_mac.sh' to launch."
echo "==================================================="
