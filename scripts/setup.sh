#!/bin/bash
set -euo pipefail

echo "=== BabyBox Setup ==="

# System packages
echo "Installing system packages..."
sudo apt update
sudo apt install -y \
    python3-pip python3-venv \
    mpv \
    pulseaudio pulseaudio-module-bluetooth \
    bluez \
    yt-dlp

# Enable SPI for MFRC522
echo "Enabling SPI..."
sudo raspi-config nonint do_spi 0

# Create media directories
echo "Creating media directories..."
mkdir -p /home/pi/babybox/media/{audio,video,thumbnails}

# Install Python dependencies
echo "Installing Python packages..."
cd /home/pi/babybox
python3 -m pip install --user flask python-mpv yt-dlp mfrc522 rpi_ws281x RPi.GPIO

# Install systemd services
echo "Installing systemd services..."
sudo cp /home/pi/babybox/scripts/babybox.service /etc/systemd/system/
sudo cp /home/pi/babybox/scripts/bt-connect.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable babybox.service
sudo systemctl enable bt-connect.service

# Ensure user is in required groups
sudo usermod -aG spi,gpio,bluetooth,audio pi

echo ""
echo "=== Setup complete! ==="
echo "1. Copy the software/ folder to /home/pi/babybox/"
echo "2. Reboot: sudo reboot"
echo "3. Web UI will be at http://babybox.local:5000"
