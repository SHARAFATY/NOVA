from pynput import keyboard as pynput_keyboard
import threading

class HotkeyListener:
    def __init__(self, hotkey="<ctrl>+;", on_hotkey=None):
        self.hotkey = hotkey
        self.on_hotkey = on_hotkey
        self.listener = None

    def start(self):
        self.listener = pynput_keyboard.GlobalHotKeys({
            self.hotkey: self._trigger
        })
        self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()

    def _trigger(self):
        if self.on_hotkey:
            self.on_hotkey() 