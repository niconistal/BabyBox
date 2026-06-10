import logging
import subprocess
import time
from typing import Optional

logger = logging.getLogger(__name__)

# How long to wait for the Bluetooth audio sink to appear after connecting
SINK_WAIT_S = 10


def _run(cmd: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _prepare_adapter():
    """Power on the adapter and register a Just-Works agent for headless pairing."""
    for sub in (["power", "on"], ["agent", "NoInputNoOutput"], ["pairable", "on"]):
        try:
            _run(["bluetoothctl", *sub], timeout=5)
        except Exception as e:
            logger.warning("bluetoothctl %s failed: %s", " ".join(sub), e)


def scan_devices(timeout: int = 10) -> list[dict]:
    """Scan for nearby Bluetooth devices. Returns list of {mac, name}."""
    _prepare_adapter()
    try:
        # --timeout runs discovery for N seconds, then exits cleanly
        _run(
            ["bluetoothctl", "--timeout", str(timeout), "scan", "on"],
            timeout=timeout + 5,
        )
    except subprocess.TimeoutExpired:
        pass  # Older bluez without --timeout: scan was killed, devices remain

    # List discovered devices
    result = _run(["bluetoothctl", "devices"], timeout=5)
    devices = []
    for line in result.stdout.strip().splitlines():
        # Format: "Device AA:BB:CC:DD:EE:FF Device Name"
        parts = line.split(" ", 2)
        if len(parts) >= 3 and parts[0] == "Device":
            devices.append({"mac": parts[1], "name": parts[2]})
    return devices


def is_connected(mac: str) -> bool:
    """Check whether a device is currently connected."""
    try:
        result = _run(["bluetoothctl", "info", mac], timeout=5)
        return "Connected: yes" in result.stdout
    except Exception:
        return False


def pair_and_connect(mac: str) -> tuple[bool, str]:
    """Pair, trust, and connect to a Bluetooth device.

    Returns (success, error_message). error_message is "" on success.
    """
    _prepare_adapter()
    try:
        for step, ok_markers in (
            ("pair", ("Pairing successful", "Already paired", "AlreadyExists")),
            ("trust", ("trust succeeded",)),
            ("connect", ("Connection successful",)),
        ):
            result = _run(["bluetoothctl", step, mac], timeout=30)
            out = (result.stdout + result.stderr).strip()
            logger.info(
                "bluetoothctl %s %s -> rc=%d %s", step, mac, result.returncode, out
            )
            ok = result.returncode == 0 or any(m in out for m in ok_markers)
            if not ok:
                if "br-connection-profile-unavailable" in out:
                    return False, (
                        "A2DP profile unavailable — PulseAudio is not running "
                        "or not reachable. Re-run scripts/setup.sh and reboot."
                    )
                last_line = out.splitlines()[-1] if out else "unknown error"
                return False, f"{step} failed: {last_line}"
        if not is_connected(mac):
            return False, "Device did not stay connected"
        return True, ""
    except subprocess.TimeoutExpired:
        logger.error("Bluetooth %s timed out", mac)
        return False, "Timed out talking to the Bluetooth adapter"
    except Exception as e:
        logger.error("Bluetooth pair/connect failed: %s", e)
        return False, str(e)


def _find_bt_sink(mac: str, wait_s: int = SINK_WAIT_S) -> Optional[str]:
    """Find the audio sink for a BT device, waiting for it to register.

    The sink appears a moment after the connection, and its name depends on
    the stack: bluez_sink.<MAC>.a2dp_sink (PulseAudio) vs
    bluez_output.<MAC>.1 (PipeWire) — so match on the MAC, not a fixed name.
    """
    needle = mac.replace(":", "_").upper()
    deadline = time.monotonic() + wait_s
    while True:
        try:
            result = _run(["pactl", "list", "short", "sinks"], timeout=5)
            for line in result.stdout.splitlines():
                fields = line.split("\t")
                if len(fields) >= 2 and needle in fields[1].upper():
                    return fields[1]
        except Exception as e:
            logger.warning("pactl list sinks failed: %s", e)
        if time.monotonic() >= deadline:
            return None
        time.sleep(1)


def set_default_sink(mac: str) -> bool:
    """Set a Bluetooth device as the default audio sink."""
    sink_name = _find_bt_sink(mac)
    if not sink_name:
        logger.error(
            "No audio sink appeared for %s — is PulseAudio running?", mac
        )
        return False
    try:
        result = _run(["pactl", "set-default-sink", sink_name], timeout=5)
        if result.returncode == 0:
            logger.info("Default sink set to %s", sink_name)
            return True
        logger.error("pactl failed: %s", result.stderr)
        return False
    except Exception as e:
        logger.error("Failed to set default sink: %s", e)
        return False


def connect_saved_speaker(mac: str, attempts: int = 3, delay: int = 5) -> bool:
    """Connect to a previously paired speaker and set as default sink.

    Retries because the speaker may still be booting or briefly out of range,
    and because WiFi/BT share one radio on the Pi Zero 2 W so single attempts
    can time out under WiFi load.
    """
    if not mac:
        return False
    _prepare_adapter()
    for attempt in range(1, attempts + 1):
        try:
            result = _run(["bluetoothctl", "connect", mac], timeout=30)
            out = (result.stdout + result.stderr).strip()
            if (
                result.returncode == 0
                or "Connection successful" in out
                or is_connected(mac)
            ):
                if not set_default_sink(mac):
                    logger.warning(
                        "Connected to %s but could not set default sink", mac
                    )
                return True
            logger.warning(
                "Connect attempt %d/%d to %s failed: %s",
                attempt, attempts, mac, out,
            )
        except Exception as e:
            logger.warning(
                "Connect attempt %d/%d to %s error: %s", attempt, attempts, mac, e
            )
        if attempt < attempts:
            time.sleep(delay)
    logger.error("Giving up on %s after %d attempts", mac, attempts)
    return False
