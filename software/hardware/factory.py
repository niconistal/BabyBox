from software.config import IS_PI
from software.hardware.base import Buzzer, ButtonHandler, LEDStrip, RFIDReader


def create_rfid() -> RFIDReader:
    if IS_PI:
        from software.hardware.real.rfid import PiRFIDReader
        return PiRFIDReader()
    from software.hardware.mock.rfid import MockRFIDReader
    return MockRFIDReader()


def create_leds() -> LEDStrip:
    if IS_PI:
        from software.hardware.real.leds import PiLEDStrip
        return PiLEDStrip()
    from software.hardware.mock.leds import MockLEDStrip
    return MockLEDStrip()


def create_buzzer() -> Buzzer:
    if IS_PI:
        from software.hardware.real.buzzer import PiBuzzer
        return PiBuzzer()
    from software.hardware.mock.buzzer import MockBuzzer
    return MockBuzzer()


def create_buttons() -> ButtonHandler:
    if IS_PI:
        from software.hardware.real.buttons import PiButtonHandler
        return PiButtonHandler()
    from software.hardware.mock.buttons import MockButtonHandler
    return MockButtonHandler()


def create_all() -> tuple[RFIDReader, LEDStrip, Buzzer, ButtonHandler]:
    return create_rfid(), create_leds(), create_buzzer(), create_buttons()
