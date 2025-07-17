import queue
import sounddevice as sd
import vosk
import json
import threading

class VoiceListener:
    def __init__(self, wake_word=None, on_wake=None, on_command=None, set_avatar_state=None):
        self.wake_word = wake_word.lower() if wake_word else None
        self.on_wake = on_wake
        self.on_command = on_command
        self.set_avatar_state = set_avatar_state
        self.model = vosk.Model(lang="en-us")
        self.samplerate = 16000
        self.q = queue.Queue()
        self.listening = False
        self.thread = None

    def _audio_callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def start_listening(self):
        self.listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def stop_listening(self):
        self.listening = False
        if self.thread:
            self.thread.join()

    def _listen_loop(self):
        rec = vosk.KaldiRecognizer(self.model, self.samplerate)
        if self.set_avatar_state:
            self.set_avatar_state('listening')
        print("[NOVA] VoiceListener: Always listening for commands...")
        with sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, dtype='int16', channels=1, callback=self._audio_callback):
            while self.listening:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text', '').strip()
                    if text:
                        print(f"[NOVA] Heard: {text}")
                        if self.set_avatar_state:
                            self.set_avatar_state('thinking')
                        if self.on_command:
                            self.on_command(text)
                        if self.set_avatar_state:
                            self.set_avatar_state('listening') 