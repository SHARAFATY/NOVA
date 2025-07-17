import sys
from core import config
from core.engine import NovaEngine
from ui.nova_ui import NovaUI
from voice.voice_listener import VoiceListener
import threading


def main():
    engine = NovaEngine()
    app = None
    ui = None

    def on_wake():
        if ui:
            ui.show_and_focus()

    def on_command(cmd):
        if ui:
            ui.accept_voice_command(cmd)

    def start_ui():
        nonlocal app, ui
        app = NovaUI(engine)
        ui = app
        app.run()

    # Start voice listener in background
    listener = VoiceListener(on_wake=on_wake, on_command=on_command)
    threading.Thread(target=listener.start_listening, daemon=True).start()

    # Start UI (main thread)
    start_ui()


if __name__ == "__main__":
    main() 