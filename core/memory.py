import json
import os
from core import config

class Memory:
    def __init__(self):
        self.path = config.MEMORY_PATH
        self.data = self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def clear(self):
        self.data = {}
        self.save() 