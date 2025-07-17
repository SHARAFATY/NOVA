import importlib
import re
from core.memory import Memory
from core.brain import Brain
from core import config
import os
import datetime

class NovaEngine:
    def __init__(self):
        self.memory = Memory()
        self.brain = Brain()
        self.log_path = config.LOGS_PATH
        self.tools = self.load_tools()

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
        command = command.strip().lower()
        self.memory.data.setdefault('history', []).append({"command": command, "time": str(datetime.datetime.now())})
        self.memory.save()
        self.brain.update(command)
        # Simple intent matching
        if any(x in command for x in ["reboot", "restart system"]):
            result = self.tools['system'].reboot()
        elif any(x in command for x in ["shutdown", "power off"]):
            result = self.tools['system'].shutdown()
        elif "update" in command:
            result = self.tools['system'].update()
        elif "uptime" in command:
            result = self.tools['system'].uptime()
        elif command.startswith("run ") or command.startswith("exec "):
            cmd = command.split(" ", 1)[1]
            result = self.tools['terminal'].run_terminal_command(cmd)
        elif "search file" in command or "find file" in command:
            pattern = command.split("file", 1)[1].strip()
            result = self.tools['files'].search_files("/", pattern)
        elif "read file" in command:
            path = command.split("read file", 1)[1].strip()
            result = self.tools['files'].read_file(path)
        elif "delete file" in command:
            path = command.split("delete file", 1)[1].strip()
            result = self.tools['files'].delete_file(path)
        elif "create file" in command:
            path = command.split("create file", 1)[1].strip()
            result = self.tools['files'].create_file(path)
        elif "ping" in command:
            host = command.split("ping", 1)[1].strip()
            result = self.tools['network'].ping(host)
        elif "scan port" in command:
            host = command.split("scan port", 1)[1].strip()
            result = self.tools['network'].port_scan(host)
        elif "public ip" in command or "my ip" in command:
            result = self.tools['network'].public_ip()
        elif "list users" in command:
            result = self.tools['users'].list_users()
        elif "change password" in command:
            m = re.match(r"change password (\w+) (.+)", command)
            if m:
                result = self.tools['users'].change_password(m.group(1), m.group(2))
            else:
                result = {"status": "error", "message": "Usage: change password <user> <newpass>"}
        elif "switch user" in command:
            user = command.split("switch user", 1)[1].strip()
            result = self.tools['users'].switch_user(user)
        elif "list processes" in command:
            result = self.tools['processes'].list_processes()
        elif "kill process" in command:
            pid = int(command.split("kill process", 1)[1].strip())
            result = self.tools['processes'].kill_process(pid)
        elif "monitor process" in command:
            pid = int(command.split("monitor process", 1)[1].strip())
            result = self.tools['processes'].monitor_process(pid)
        elif "cpu usage" in command:
            result = self.tools['monitor'].cpu_usage()
        elif "ram usage" in command or "memory usage" in command:
            result = self.tools['monitor'].ram_usage()
        elif "disk usage" in command:
            result = self.tools['monitor'].disk_usage()
        elif "clear memory" in command:
            self.memory.clear()
            result = {"status": "ok", "message": "Memory cleared."}
        elif "show logs" in command:
            today = datetime.date.today()
            log_file = os.path.join(self.log_path, f'{today}.log')
            if os.path.exists(log_file):
                with open(log_file) as f:
                    logs = f.read()
                result = {"status": "ok", "message": logs}
            else:
                result = {"status": "ok", "message": "No logs for today."}
        elif "what can you do" in command or "list capabilities" in command:
            result = {"status": "ok", "message": ", ".join(self.tools.keys())}
        elif "what did i do" in command:
            # Example: what did I do last friday
            result = self._history_summary(command)
        else:
            result = {"status": "error", "message": "I can learn this if you show me once."}
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