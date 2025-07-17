from core import config
from core.engine import NovaEngine
from voice.voice_listener import VoiceListener
from voice.text_to_speech import get_tts
import threading
import sys


def main():
    engine = NovaEngine()

    def on_wake():
        print("[NOVA] Wake word detected. Listening for command...")

    def on_command(cmd):
        print(f"[NOVA] Command: {cmd}")
        result = engine.handle_command(cmd)
        print(f"[NOVA] Result: {result.get('message', str(result))}")
        get_tts().speak(result.get("message", str(result)))

    # Start voice listener in background
    listener = VoiceListener(on_wake=on_wake, on_command=on_command)
    listener.start_listening()
    # Keep the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("[NOVA] Shutting down.")

if __name__ == "__main__":
    main() 