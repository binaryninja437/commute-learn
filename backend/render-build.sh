#!/usr/bin/env bash
# Render build script for SaarLM backend

set -o errexit  # Exit on error

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Installing ffmpeg for audio processing..."
apt-get update
apt-get install -y ffmpeg

echo "Build complete!"
