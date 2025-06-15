from RPi import GPIO
from playsound3 import playsound
from pathlib import Path
from time import sleep
import random

AUDIO_FOLDER = Path("audio/")
DEBUG = True
PIN = 16

# Set GPIO mode to BCM
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# magnet = Button(PIN)


class Door:
    def __init__(self, state: str = "closed") -> None:
        self.state = state

    def switch_state(self, new_state) -> None:
        if new_state == "open":
            self.state = "open"
        elif new_state == "closed":
            self.state = "closed"
        else:
            raise RuntimeError("Somehow we got a nonexistent state.")


def get_current_state(*, debug: bool = False) -> str:
    if debug:
        # NOTE: the magnets "are touching" if the file exists
        magnet_file = Path("magnet")
        magnets_are_connected: bool = magnet_file.exists()
    else:
        try:
            magnet = GPIO.input(PIN)
            if magnet == GPIO.HIGH:
                magnets_are_connected = False
            else:
                magnets_are_connected = True
        except Exception:
            GPIO.cleanup()

    if magnets_are_connected:
        return "closed"
    else:
        return "open"


def main():
    sound_library = [s for s in AUDIO_FOLDER.iterdir() if s.name != ".gitkeep"]
    door = Door(get_current_state(debug=DEBUG))
    while True:
        new_state = get_current_state(debug=DEBUG)

        if door.state != new_state:
            door.switch_state(new_state)

            # door just opened
            if new_state == "open":
                chosen_sound = random.choice(sound_library)
                playsound(chosen_sound)

        sleep(1)  # seconds


if __name__ == "__main__":
    main()
