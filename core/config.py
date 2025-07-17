import os

NOVA_NAME = "NOVA"
MEMORY_PATH = os.path.join(os.path.dirname(__file__), '../memory/memory.json')
LOGS_PATH = os.path.join(os.path.dirname(__file__), '../memory/logs/')
VOICE = {
    "rate": 160,
    "volume": 1.0,
    "voice_id": None  # To be set by TTS engine
}
UI_THEME = "neon_glass" 