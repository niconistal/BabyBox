#!/bin/bash
set -euo pipefail

echo "=== BabyBox Setup ==="

# System packages
echo "Installing system packages..."
sudo apt update
# Note: yt-dlp is intentionally NOT installed from apt — the packaged version
# is frozen and goes stale within weeks as YouTube changes, breaking downloads
# (SABR / signature-extraction errors). We install the current standalone
# binary below instead. mpv pulls in ffmpeg, which yt-dlp needs for audio
# extraction. libmpv-dev provides the libmpv shared library: the player uses
# the python-mpv binding, which dlopen's libmpv at runtime, and the mpv CLI
# package alone does NOT install it on Trixie (playback fails with "Cannot
# find libmpv in the usual places").
sudo apt install -y \
    python3-pip python3-venv \
    mpv libmpv-dev \
    pulseaudio pulseaudio-module-bluetooth \
    bluez \
    iw \
    curl unzip

# Enable SPI for MFRC522
echo "Enabling SPI..."
sudo raspi-config nonint do_spi 0

# Raspberry Pi OS can leave the Bluetooth radio rfkill soft-blocked on a fresh
# image. While blocked the adapter is "off-blocked" and `bluetoothctl power on`
# (which the speaker scan/connect relies on) silently fails, so no devices are
# ever found. Unblock it; systemd-rfkill persists this across reboots.
echo "Unblocking Bluetooth radio (rfkill)..."
sudo rfkill unblock bluetooth

# yt-dlp + JS runtime. The app calls bare `yt-dlp` via PATH, so install the
# current standalone binary into /usr/local/bin (ahead of any apt copy on the
# default systemd PATH). Modern yt-dlp also needs a JavaScript runtime to solve
# YouTube's signature challenges — without one it falls back to limited clients
# and fails with "This video is not available". deno is yt-dlp's default,
# auto-detected runtime. Run `yt-dlp -U` periodically to keep it current.
echo "Installing yt-dlp (latest) + deno JS runtime..."
ARCH=$(uname -m)
case "$ARCH" in
    aarch64) YTDLP_ASSET=yt-dlp_linux_aarch64; DENO_ASSET=deno-aarch64-unknown-linux-gnu.zip ;;
    armv7l)  YTDLP_ASSET=yt-dlp_linux_armv7l; DENO_ASSET="" ;;
    x86_64)  YTDLP_ASSET=yt-dlp_linux;         DENO_ASSET=deno-x86_64-unknown-linux-gnu.zip ;;
    *)       YTDLP_ASSET=yt-dlp;               DENO_ASSET="" ;;
esac
sudo curl -fL --retry 3 -o /usr/local/bin/yt-dlp \
    "https://github.com/yt-dlp/yt-dlp/releases/latest/download/$YTDLP_ASSET"
sudo chmod 0755 /usr/local/bin/yt-dlp
if [ -n "$DENO_ASSET" ]; then
    curl -fL --retry 3 -o /tmp/deno.zip \
        "https://github.com/denoland/deno/releases/latest/download/$DENO_ASSET"
    rm -rf /tmp/deno-extract
    python3 -c "import zipfile; zipfile.ZipFile('/tmp/deno.zip').extractall('/tmp/deno-extract')"
    sudo install -m 0755 /tmp/deno-extract/deno /usr/local/bin/deno
    rm -rf /tmp/deno.zip /tmp/deno-extract
else
    echo "WARNING: no deno build for $ARCH — YouTube downloads may fail without a JS runtime."
fi

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
python3 -m pip install --user --break-system-packages flask python-mpv mfrc522 rpi_ws281x RPi.GPIO

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
