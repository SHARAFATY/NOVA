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

EXAMPLES = [
    "reboot (restarts your computer)",
    "shutdown (powers off your computer)",
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

def friendly_reply(text):
    if not text.strip():
        return "I'm here if you need anything!"
    prefix = random.choice(FRIENDLY_PREFIXES)
    return prefix + text

class NovaEngine:
    def __init__(self):
        self.memory = Memory()
        self.brain = Brain()
        self.log_path = config.LOGS_PATH
        self.tools = self.load_tools()
        self.awaiting_confirmation = None
        self.awaiting_command = None

    def load_tools(self):
        # Dynamically import all tool modules
        tool_dir = os.path.join(os.path.dirname(__file__), '../tools')
        tool_modules = {}
        for fname in os.listdir(tool_dir):
            if fname.endswith('.py') and fname != '__init__.py':
                mod_name = fname[:-3]
                tool_modules[mod_name] = importlib.import_module(f'tools.{mod_name}')
            elif os.path.isdir(os.path.join(tool_dir, fname)) and fname == 'custom':
                # Load custom tools
                custom_dir = os.path.join(tool_dir, 'custom')
                for cf in os.listdir(custom_dir):
                    if cf.endswith('.py') and cf != '__init__.py':
                        mod_name = f'custom.{cf[:-3]}'
                        tool_modules[mod_name] = importlib.import_module(f'tools.custom.{cf[:-3]}')
        return tool_modules

    def log_action(self, command, result):
        os.makedirs(self.log_path, exist_ok=True)
        log_file = os.path.join(self.log_path, f'{datetime.date.today()}.log')
        with open(log_file, 'a') as f:
            f.write(f"[{datetime.datetime.now()}] {command} => {result}\n")

    def handle_command(self, command: str) -> dict:
        command = command.strip()
        command_lower = command.lower()
        # Remove "nova" from the start if present
        if command_lower.startswith("nova "):
            command_lower = command_lower[5:]
            command = command[5:]
        # Security confirmation logic
        if self.awaiting_confirmation:
            if command in ["yes", "confirm", "proceed"]:
                orig_command = self.awaiting_command
                self.awaiting_confirmation = None
                self.awaiting_command = None
                return self.handle_command(orig_command + " --confirmed")
            elif command in ["no", "cancel", "abort"]:
                self.awaiting_confirmation = None
                self.awaiting_command = None
                return {"status": "ok", "message": "Action cancelled."}
            else:
                return {"status": "error", "message": "Please say 'yes' to confirm or 'no' to cancel."}
        self.memory.data.setdefault('history', []).append({"command": command, "time": str(datetime.datetime.now())})
        self.memory.save()
        self.brain.update(command)
        # Fuzzy/intent matching for natural language
        if fuzz.partial_ratio(command_lower, "what time is it") > 80 or re.search(r"\btime\b", command_lower):
            now = datetime.datetime.now().strftime("%H:%M:%S")
            result = {"status": "ok", "message": friendly_reply(f"The current time is {now}.")}
        elif fuzz.partial_ratio(command_lower, "weather") > 80 or re.search(r"weather|forecast|temperature", command_lower):
            try:
                output = subprocess.check_output(["curl", "-s", "wttr.in?format=3"], text=True, timeout=10)
                result = {"status": "ok", "message": friendly_reply(output.strip())}
            except Exception as e:
                result = {"status": "error", "message": friendly_reply(f"Could not get weather: {e}")}
        elif re.match(r"open (.+)", command_lower):
            prog = re.match(r"open (.+)", command_lower).group(1).strip()
            try:
                subprocess.Popen([prog])
                result = {"status": "ok", "message": friendly_reply(f"Opened {prog}.")}
            except Exception as e:
                result = {"status": "error", "message": friendly_reply(f"Could not open {prog}: {e}")}
        elif re.search(r"nmap", command_lower):
            # e.g. "run deep nmap scan on 192.168.1.1"
            match = re.search(r"nmap(.*)", command_lower)
            args = match.group(1).strip() if match else ""
            try:
                output = subprocess.check_output(["nmap"] + args.split(), text=True, timeout=30)
                result = {"status": "ok", "message": friendly_reply(output)}
            except Exception as e:
                result = {"status": "error", "message": friendly_reply(f"nmap error: {e}")}
        elif re.search(r"sqlmap", command_lower):
            match = re.search(r"sqlmap(.*)", command_lower)
            args = match.group(1).strip() if match else ""
            try:
                output = subprocess.check_output(["sqlmap"] + args.split(), text=True, timeout=60)
                result = {"status": "ok", "message": friendly_reply(output)}
            except Exception as e:
                result = {"status": "error", "message": friendly_reply(f"sqlmap error: {e}")}
        elif any(fuzz.partial_ratio(command_lower, kw) > 80 for kw in ["reboot", "restart system"]):
            if "--confirmed" not in command_lower:
                self.awaiting_confirmation = True
                self.awaiting_command = command
                return {"status": "confirm", "message": friendly_reply("Are you sure you want to reboot? Say 'yes' or 'no'.")}
            result = self.tools['system'].reboot()
            result["message"] = friendly_reply(result["message"])
        elif any(fuzz.partial_ratio(command_lower, kw) > 80 for kw in ["shutdown", "power off"]):
            if "--confirmed" not in command_lower:
                self.awaiting_confirmation = True
                self.awaiting_command = command
                return {"status": "confirm", "message": friendly_reply("Are you sure you want to shutdown? Say 'yes' or 'no'.")}
            result = self.tools['system'].shutdown()
            result["message"] = friendly_reply(result["message"])
        elif re.match(r"run (.+)", command_lower):
            cmd = re.match(r"run (.+)", command_lower).group(1)
            result = self.tools['terminal'].run_terminal_command(cmd)
            result["message"] = friendly_reply(result.get("output", ""))
        elif re.match(r"who are you|what are you|your name", command_lower):
            result = {"status": "ok", "message": friendly_reply("I'm NOVA, your local Linux assistant. How can I help you today?")}
        elif re.match(r"hi|hello|hey|how are you|good morning|good evening|good night", command_lower):
            result = {"status": "ok", "message": friendly_reply("Hello! How can I help you?")}
        elif "what can you do" in command_lower or "help" in command_lower or "list capabilities" in command_lower:
            result = {
                "status": "ok",
                "message": friendly_reply("I can do:\n" + "\n".join(EXAMPLES))
            }
        elif command_lower.strip() == "":
            result = {"status": "ok", "message": friendly_reply("")}
        elif "search file" in command_lower or "find file" in command_lower:
            pattern = command_lower.split("file", 1)[1].strip()
            result = self.tools['files'].search_files("/", pattern)
        elif "read file" in command_lower:
            path = command_lower.split("read file", 1)[1].strip()
            result = self.tools['files'].read_file(path)
        elif "delete file" in command_lower:
            if "--confirmed" not in command_lower:
                self.awaiting_confirmation = True
                self.awaiting_command = command
                return {"status": "confirm", "message": "Are you sure you want to delete this file? Say 'yes' or 'no'."}
            path = command_lower.split("delete file", 1)[1].replace("--confirmed", "").strip()
            result = self.tools['files'].delete_file(path)
        elif "create file" in command_lower:
            path = command_lower.split("create file", 1)[1].strip()
            result = self.tools['files'].create_file(path)
        elif "ping" in command_lower:
            host = command_lower.split("ping", 1)[1].strip()
            result = self.tools['network'].ping(host)
        elif "scan port" in command_lower:
            host = command_lower.split("scan port", 1)[1].strip()
            result = self.tools['network'].port_scan(host)
        elif "public ip" in command_lower or "my ip" in command_lower:
            result = self.tools['network'].public_ip()
        elif "list users" in command_lower:
            result = self.tools['users'].list_users()
        elif "change password" in command_lower:
            m = re.match(r"change password (\w+) (.+)", command_lower)
            if m:
                result = self.tools['users'].change_password(m.group(1), m.group(2))
            else:
                result = {"status": "error", "message": "Usage: change password <user> <newpass>"}
        elif "switch user" in command_lower:
            user = command_lower.split("switch user", 1)[1].strip()
            result = self.tools['users'].switch_user(user)
        elif "list processes" in command_lower:
            result = self.tools['processes'].list_processes()
        elif "kill process" in command_lower:
            pid = int(command_lower.split("kill process", 1)[1].strip())
            result = self.tools['processes'].kill_process(pid)
        elif "monitor process" in command_lower:
            pid = int(command_lower.split("monitor process", 1)[1].strip())
            result = self.tools['processes'].monitor_process(pid)
        elif "cpu usage" in command_lower:
            result = self.tools['monitor'].cpu_usage()
        elif "ram usage" in command_lower or "memory usage" in command_lower:
            result = self.tools['monitor'].ram_usage()
        elif "disk usage" in command_lower:
            result = self.tools['monitor'].disk_usage()
        elif "clear memory" in command_lower:
            self.memory.clear()
            result = {"status": "ok", "message": "Memory cleared."}
        elif "show logs" in command_lower:
            today = datetime.date.today()
            log_file = os.path.join(self.log_path, f'{today}.log')
            if os.path.exists(log_file):
                with open(log_file) as f:
                    logs = f.read()
                result = {"status": "ok", "message": logs}
            else:
                result = {"status": "ok", "message": "No logs for today."}
        elif "what did i do" in command_lower:
            # Example: what did I do last friday
            result = self._history_summary(command)
        else:
            # Chatty fallback
            result = {"status": "ok", "message": friendly_reply("I'm here to help! You can ask me to open programs, run scans, or just chat.")}
        self.log_action(command, result)
        return result

    def _history_summary(self, command):
        # Simple history summary for demo
        hist = self.memory.data.get('history', [])
        if not hist:
            return {"status": "ok", "message": "No history found."}
        # TODO: parse date from command
        last = hist[-5:]
        summary = "\n".join([f"{h['time']}: {h['command']}" for h in last])
        return {"status": "ok", "message": summary} 