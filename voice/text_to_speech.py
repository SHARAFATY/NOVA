import pyttsx3
from core import config

try:
    from rhvoice_wrapper import RHVoice
    rhvoice_available = True
except ImportError:
    rhvoice_available = False

class TextToSpeech:
    def __init__(self):
        self.use_rhvoice = rhvoice_available
        if self.use_rhvoice:
            self.tts = RHVoice()
            # Use a female English voice if available
            self.voice = "anna" if "anna" in self.tts.voices else self.tts.voices[0]
        else:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', config.VOICE['rate'])
            self.engine.setProperty('volume', config.VOICE['volume'])
            # Try to select a female, human-like voice
            voices = self.engine.getProperty('voices')
            for v in voices:
                if 'female' in v.name.lower() or 'female' in v.id.lower():
                    self.engine.setProperty('voice', v.id)
                    break
        # For more natural speech, consider using Coqui TTS (https://github.com/coqui-ai/TTS)

    def speak(self, text):
        if self.use_rhvoice:
            self.tts.say(text, voice=self.voice)
        else:
            self.engine.say(text)
            self.engine.runAndWait()

# Singleton instance for global use
_tts = None
def get_tts():
    global _tts
    if _tts is None:
        _tts = TextToSpeech()
    return _tts 