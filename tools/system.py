import subprocess
import platform

def reboot() -> dict:
    try:
        subprocess.Popen(['sudo', 'reboot'])
        return {"status": "ok", "message": "Rebooting system..."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def shutdown() -> dict:
    try:
        subprocess.Popen(['sudo', 'shutdown', 'now'])
        return {"status": "ok", "message": "Shutting down system..."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def update() -> dict:
    try:
        result = subprocess.run(['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'upgrade', '-y'], shell=True, capture_output=True, text=True)
        return {"status": "ok", "message": result.stdout.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def uptime() -> dict:
    try:
        result = subprocess.run(['uptime', '-p'], capture_output=True, text=True)
        return {"status": "ok", "message": result.stdout.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)} 