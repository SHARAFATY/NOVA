import subprocess
import socket
import requests

def ping(host) -> dict:
    try:
        result = subprocess.run(["ping", "-c", "2", host], capture_output=True, text=True)
        return {"status": "ok", "output": result.stdout.strip()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def port_scan(host, ports=[22, 80, 443]) -> dict:
    open_ports = []
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect((host, port))
            open_ports.append(port)
        except:
            pass
        s.close()
    return {"status": "ok", "open_ports": open_ports}

def public_ip() -> dict:
    try:
        ip = requests.get('https://api.ipify.org').text
        return {"status": "ok", "ip": ip}
    except Exception as e:
        return {"status": "error", "message": str(e)} 