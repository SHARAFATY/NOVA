import importlib
import re
from core.memory import Memory
from core.brain import Brain
from core import config
import os
import datetime
import subprocess
from rapidfuzz import fuzz, process
import random
from sentence_transformers import SentenceTransformer, util
from core.ollama_client import OllamaClient

EXAMPLES = [
    "reboot (restarts your computer)",
    "shutdown (restarts your computer)",
    "update (runs system update)",
    "uptime (shows how long your system has been running)",
    "run <command> (runs any terminal command)",
    "search file <pattern> (finds files)",
    "read file <path> (shows file content)",
    "delete file <path> (removes a file, asks for confirmation)",
    "ping <host> (network test)",
    "public ip (shows your public IP address)",
    "list users (shows all system users)",
    "change password <user> <newpass>",
    "switch user <user>",
    "list processes",
    "kill process <pid>",
    "cpu usage / ram usage / disk usage",
    "clear memory (clears assistant memory)",
    "show logs (shows today's logs)",
    "what did I do last friday (shows your command history)",
    "what time is it / current time",
    "weather / what's the weather",
    "open <program> (launches a program)",
    "run nmap <args> (network scan)",
    "run sqlmap <args> (SQL injection test)",
    "You can also just chat with me!"
]

FRIENDLY_PREFIXES = [
    "Of course! ",
    "Sure! ",
    "Absolutely! ",
    "Right away! ",
    "Here's what I found: ",
    "No problem! ",
    "Happy to help! ",
    "Alright! ",
    "You got it! ",
    "Let me check... ",
    "Here's the info: ",
    "Done! ",
]

CLARIFICATION_RESPONSES = [
    "Sorry, I didn't catch that. Could you repeat?",
    "I'm not sure I understood. Would you like to try again or ask for help?",
    "Could you rephrase that for me?",
    "Could you say that another way?",
    "I want to help, but I didn't quite get that.",
    "Hmm, that didn't sound like a command I know. Want an example?",
]

SMALL_TALK_RESPONSES = [
    "I'm always here if you want to chat!",
    "Let me know if you need anything else.",
    "You can ask me to open programs, run scans, or just chat!",
    "If you want to teach me something new, just say so!",
]

FRUSTRATION_KEYWORDS = ["boring", "not working", "useless", "dumb", "annoying", "frustrated", "hate"]

NAME_PATTERNS = [
    re.compile(r"my name is ([a-zA-Z0-9_\- ]+)", re.I),
    re.compile(r"call me ([a-zA-Z0-9_\- ]+)", re.I),
    re.compile(r"i am ([a-zA-Z0-9_\- ]+)", re.I),
]

# For intent detection
INTENT_COMMANDS = [
    "reboot",
    "shutdown",
    "update",
    "uptime",
    "run terminal command",
    "search file",
    "read file",
    "delete file",
    "create file",
    "ping",
    "public ip",
    "list users",
    "change password",
    "switch user",
    "list processes",
    "kill process",
    "monitor process",
    "cpu usage",
    "ram usage",
    "disk usage",
    "clear memory",
    "show logs",
    "history",
    "time",
    "weather",
    "open program",
    "run nmap",
    "run sqlmap",
    "help",
    "chat",
]

INTENT_PATTERNS = {
    "reboot": ["reboot", "restart system", "restart computer"],
    "shutdown": ["shutdown", "power off", "turn off"],
    "update": ["update", "system update", "upgrade"],
    "uptime": ["uptime", "how long running"],
    "run terminal command": ["run ", "exec "],
    "search file": ["search file", "find file"],
    "read file": ["read file"],
    "delete file": ["delete file"],
    "create file": ["create file"],
    "ping": ["ping"],
    "public ip": ["public ip", "my ip"],
    "list users": ["list users"],
    "change password": ["change password"],
    "switch user": ["switch user"],
    "list processes": ["list processes"],
    "kill process": ["kill process"],
    "monitor process": ["monitor process"],
    "cpu usage": ["cpu usage"],
    "ram usage": ["ram usage", "memory usage"],
    "disk usage": ["disk usage"],
    "clear memory": ["clear memory"],
    "show logs": ["show logs"],
    "history": ["what did i do"],
    "time": ["what time is it", "current time", "time"],
    "weather": ["weather", "forecast", "temperature"],
    "open program": ["open "],
    "run nmap": ["nmap"],
    "run sqlmap": ["sqlmap"],
    "help": ["what can you do", "help", "list capabilities"],
    "chat": ["hi", "hello", "hey", "how are you", "good morning", "good evening", "good night", "who are you", "your name"],
}

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
intent_embs = model.encode(INTENT_COMMANDS, convert_to_tensor=True)

def detect_intent(user_input):
    emb = model.encode(user_input, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(emb, intent_embs)[0]
    best_idx = int(scores.argmax())
    return INTENT_COMMANDS[best_idx], float(scores[best_idx])

def friendly_reply(text):
    if not text:
        return "I'm here if you need anything!"
    prefix = random.choice(FRIENDLY_PREFIXES)
    return prefix + text

class NovaEngine:
    def __init__(self):
        self.memory = Memory()
        self.brain = Brain(memory=self.memory)
        self.log_path = config.LOGS_PATH
        self.ollama = OllamaClient()

    def log_action(self, command, result):
        os.makedirs(self.log_path, exist_ok=True)
        log_file = os.path.join(self.log_path, f'{datetime.date.today()}.log')
        with open(log_file, 'a') as f:
            f.write(f"[{datetime.datetime.now()}] {command} => {result}\n")

    def handle_command(self, command: str) -> dict:
        command = command.strip()
        name = self.brain.get_preference('user_name', 'friend')
        system_prompt = (
            f"You are NOVA, a helpful Linux AI assistant. Respond to the user's requests, including Linux commands, questions, and general conversation. "
            f"If the user asks for a command, provide the answer or the command to run. The user's name is {name}."
        )
        ollama_reply = self.ollama.generate(command, system=system_prompt)
        result = {"status": "ok", "message": friendly_reply(ollama_reply)}
        self.brain.update(command, result.get("message"))
        self.log_action(command, result)
        return result 