import subprocess

def run_terminal_command(command: str) -> dict:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "status": "ok" if result.returncode == 0 else "error",
            "output": result.stdout.strip(),
            "error": result.stderr.strip()
        }
    except Exception as e:
        return {"status": "error", "output": "", "error": str(e)} 