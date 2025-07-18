from core import config
from core.engine import TovaEngine
from voice.voice_listener import VoiceListener
from voice.text_to_speech import get_tts
import threading
import sys


def main():
    engine = TovaEngine()
    tts = get_tts()
    listener = None
    tts_lock = threading.Lock()
    
    def on_wake():
        print("[TOVA] Wake word detected. Listening for command...")

    def on_command(cmd):
        nonlocal listener
        with tts_lock:
            if tts.speaking:
                tts.stop()  # Interrupt current speech
            if listener:
                listener.stop_listening()
            print(f"[TOVA] Command: {cmd}")
            result = engine.handle_command(cmd)
            print(f"[TOVA] Result: {result.get('message', str(result))}")
            tts.speaking = True
            tts.speak(result.get("message", str(result)))
            tts.speaking = False
            if listener:
                listener.start_listening()

    # Start voice listener in background
    listener = VoiceListener(on_wake=on_wake, on_command=on_command)
    listener.start_listening()
    # Keep the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("[TOVA] Shutting down.")

if __name__ == "__main__":
    main() 