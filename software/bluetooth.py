import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


def scan_devices(timeout: int = 10) -> list[dict]:
    """Scan for nearby Bluetooth devices. Returns list of {mac, name}."""
    try:
        # Start scan
        subprocess.run(
            ["bluetoothctl", "scan", "on"],
            timeout=timeout, capture_output=True,
        )
    except subprocess.TimeoutExpired:
        pass  # Expected — scan runs until timeout

    # List discovered devices
    result = subprocess.run(
        ["bluetoothctl", "devices"],
        capture_output=True, text=True, timeout=5,
    )
    devices = []
    for line in result.stdout.strip().splitlines():
        # Format: "Device AA:BB:CC:DD:EE:FF Device Name"
        parts = line.split(" ", 2)
        if len(parts) >= 3 and parts[0] == "Device":
            devices.append({"mac": parts[1], "name": parts[2]})
    return devices


def pair_and_connect(mac: str) -> bool:
    """Pair, trust, and connect to a Bluetooth device."""
    try:
        for cmd in [
            ["bluetoothctl", "pair", mac],
            ["bluetoothctl", "trust", mac],
            ["bluetoothctl", "connect", mac],
        ]:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15,
            )
            logger.info("%s -> %s", " ".join(cmd), result.stdout.strip())
        return True
    except Exception as e:
        logger.error("Bluetooth pair/connect failed: %s", e)
        return False


def set_default_sink(mac: str) -> bool:
    """Set a Bluetooth device as the default PulseAudio sink."""
    # PulseAudio sink name format: bluez_sink.XX_XX_XX_XX_XX_XX.a2dp_sink
    sink_name = f"bluez_sink.{mac.replace(':', '_')}.a2dp_sink"
    try:
        result = subprocess.run(
            ["pactl", "set-default-sink", sink_name],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            logger.info("Default sink set to %s", sink_name)
            return True
        logger.error("pactl failed: %s", result.stderr)
        return False
    except Exception as e:
        logger.error("Failed to set default sink: %s", e)
        return False


def connect_saved_speaker(mac: str) -> bool:
    """Connect to a previously paired speaker and set as default sink."""
    if not mac:
        return False
    try:
        subprocess.run(
            ["bluetoothctl", "power", "on"],
            capture_output=True, timeout=5,
        )
        result = subprocess.run(
            ["bluetoothctl", "connect", mac],
            capture_output=True, text=True, timeout=15,
        )
        if "Connection successful" in result.stdout or result.returncode == 0:
            # Wait briefly for PulseAudio to register the sink
            import time
            time.sleep(2)
            set_default_sink(mac)
            return True
        logger.warning("Could not connect to %s: %s", mac, result.stdout)
        return False
    except Exception as e:
        logger.error("Speaker connect failed: %s", e)
        return False
