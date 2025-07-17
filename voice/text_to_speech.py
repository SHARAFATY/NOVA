import pyttsx3
from core import config

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', config.VOICE['rate'])
        self.engine.setProperty('volume', config.VOICE['volume'])
        if config.VOICE['voice_id']:
            self.engine.setProperty('voice', config.VOICE['voice_id'])

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

# Singleton instance for global use
_tts = None
def get_tts():
    global _tts
    if _tts is None:
        _tts = TextToSpeech()
    return _tts 