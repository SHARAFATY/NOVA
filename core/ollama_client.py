import requests
import json

OLLAMA_URL = 'http://localhost:11434/api/generate'

class OllamaClient:
    def __init__(self, model='tinyllama'):
        self.model = model

    def generate(self, prompt, system=None):
        payload = {
            'model': self.model,
            'prompt': prompt,
        }
        if system:
            payload['system'] = system
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=60, stream=True)
            response.raise_for_status()
            result = ''
            for line in response.iter_lines():
                if line:
                    try:
                        data = line.decode('utf-8')
                        if data.startswith('{'):
                            obj = json.loads(data)
                            if 'response' in obj:
                                result += obj['response']
                    except Exception:
                        continue
            if not result:
                return '[Ollama did not respond]'
            return result.strip()
        except Exception as e:
            return f"[Ollama error: {e}]" 