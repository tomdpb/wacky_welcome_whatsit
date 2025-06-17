from collections import deque
from RPi import GPIO
from playsound3 import playsound
from pathlib import Path
from time import sleep
import random

AUDIO_FOLDER = Path("/home/pi/wacky_welcome_whatsit/audio/")
DEBUG = False
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


def sound_cycler(sounds):
    queue = deque(sounds)
    while True:
        for _ in range(len(queue)):
            yield queue[0]
            queue.rotate(-1)
        random.shuffle(queue)


def main():
    sound_library = [s for s in AUDIO_FOLDER.iterdir() if s.name != ".gitkeep"]
    sound_generator = sound_cycler(sound_library)
    door = Door(get_current_state(debug=DEBUG))
    while True:
        new_state = get_current_state(debug=DEBUG)

        if door.state != new_state:
            door.switch_state(new_state)

            # door just opened
            if new_state == "open":
                chosen_sound = next(sound_generator)
                playsound(chosen_sound)

        sleep(1)  # seconds


if __name__ == "__main__":
    print("Running!")
    main()
