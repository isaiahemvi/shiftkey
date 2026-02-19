import random
import subprocess
import threading
from pathlib import Path

from pynput import keyboard

AUDIO_DIR = Path(__file__).parent / "audio_files"
SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".aiff", ".aif", ".m4a", ".caf"}


def load_audio_files(directory: Path) -> list[Path]:
    files = [
        f for f in directory.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if not files:
        raise FileNotFoundError(
            f"No supported audio files found in:\n  {directory}\n"
            f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    return files


def play_random_sound(audio_files: list[Path]) -> None:
    """Pick a random file and play it via afplay in a daemon thread."""
    chosen = random.choice(audio_files)
    def _play():
        try:
            subprocess.Popen(
                ["afplay", str(chosen)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            print(f"[warn] Could not play {chosen.name}: {e}")
    t = threading.Thread(target=_play, daemon=True)
    t.start()


def main():
    print(f"Loading audio files from:\n  {AUDIO_DIR}\n")
    audio_files = load_audio_files(AUDIO_DIR)
    print(f"Found {len(audio_files)} audio file(s).")
    print("Start typing — a random sound plays on each key press.")
    print("Press ESC to quit.\n")

    stop_event = threading.Event()

    def on_press(key):
        if key == keyboard.Key.esc:
            print("\nESC pressed")
            stop_event.set()
            return False  # stops the listener
        play_random_sound(audio_files)

    with keyboard.Listener(on_press=on_press) as listener:
        stop_event.wait()
        listener.stop()


if __name__ == "__main__":
    main()