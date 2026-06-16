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
    iw \
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
# --break-system-packages: Raspberry Pi OS (Bookworm+/Trixie) marks the system
# Python as externally-managed (PEP 668); --user installs are refused without it.
# Packages land in the pi user's ~/.local, which the systemd services (User=pi,
# system /usr/bin/python3) pick up via the per-user site automatically.
python3 -m pip install --user --break-system-packages flask python-mpv yt-dlp mfrc522 rpi_ws281x RPi.GPIO

# Install systemd services
echo "Installing systemd services..."
sudo cp /home/pi/babybox/scripts/babybox.service /etc/systemd/system/
sudo cp /home/pi/babybox/scripts/bt-connect.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable babybox.service
sudo systemctl enable bt-connect.service

# Ensure user is in required groups
sudo usermod -aG spi,gpio,bluetooth,audio pi

# PulseAudio runs per-user and normally only starts on login. BabyBox is
# headless, so enable lingering: the pi user's session (and PulseAudio)
# starts at boot. Without this, bluetoothd has no A2DP sink registered and
# speaker connections fail with "br-connection-profile-unavailable".
echo "Enabling user lingering so PulseAudio runs headless..."
sudo loginctl enable-linger pi
sudo systemctl --machine=pi@.host --user enable pulseaudio.socket pulseaudio.service 2>/dev/null || true

# WiFi and Bluetooth share a single 2.4GHz radio + antenna on the Pi Zero 2 W.
# WiFi power-save (on by default) starves Bluetooth and causes connect
# timeouts when both are in use. Disable it permanently.
echo "Disabling WiFi power save (WiFi/Bluetooth coexistence)..."
sudo tee /etc/systemd/system/wifi-powersave-off.service > /dev/null <<'EOF'
[Unit]
Description=Disable WiFi power save (Bluetooth coexistence)
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/iw dev wlan0 set power_save off
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable wifi-powersave-off.service

echo ""
echo "=== Setup complete! ==="
echo "1. Copy the software/ folder to /home/pi/babybox/"
echo "2. Reboot: sudo reboot"
echo "3. Web UI will be at http://babybox.local:5000"
