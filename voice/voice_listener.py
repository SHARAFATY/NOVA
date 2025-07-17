import queue
import sounddevice as sd
import vosk
import json
import threading

class VoiceListener:
    def __init__(self, wake_word="nova", on_wake=None, on_command=None, set_avatar_state=None):
        self.wake_word = wake_word.lower()
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
        print("[NOVA] VoiceListener: Waiting for wake word...")
        with sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, dtype='int16', channels=1, callback=self._audio_callback):
            while self.listening:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text', '').lower()
                    print(f"[NOVA] Heard: {text}")
                    if self.wake_word in text:
                        print("[NOVA] Wake word detected!")
                        if self.set_avatar_state:
                            self.set_avatar_state('thinking')
                        if self.on_wake:
                            self.on_wake()
                        # Listen for next command
                        if self.set_avatar_state:
                            self.set_avatar_state('listening')
                        cmd = self._listen_for_command()
                        if cmd:
                            print(f"[NOVA] Command detected: {cmd}")
                            if self.set_avatar_state:
                                self.set_avatar_state('thinking')
                            if self.on_command:
                                self.on_command(cmd)
                        if self.set_avatar_state:
                            self.set_avatar_state('idle')

    def _listen_for_command(self):
        rec = vosk.KaldiRecognizer(self.model, self.samplerate)
        print("[NOVA] Listening for command...")
        with sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000, dtype='int16', channels=1, callback=self._audio_callback):
            # Listen for a single command phrase
            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get('text', '').strip()
                    if text:
                        return text 