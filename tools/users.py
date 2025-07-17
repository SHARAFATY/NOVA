import subprocess

def list_users() -> dict:
    try:
        result = subprocess.run(['cut', '-d:', '-f1', '/etc/passwd'], capture_output=True, text=True)
        users = result.stdout.strip().split('\n')
        return {"status": "ok", "users": users}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def change_password(username, new_password) -> dict:
    try:
        cmd = f'echo "{username}:{new_password}" | sudo chpasswd'
        subprocess.run(cmd, shell=True, check=True)
        return {"status": "ok", "message": f"Password changed for {username}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def switch_user(username) -> dict:
    try:
        subprocess.run(['su', username], check=True)
        return {"status": "ok", "message": f"Switched to {username}"}
    except Exception as e:
        return {"status": "error", "message": str(e)} 