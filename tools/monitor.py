import psutil

def cpu_usage() -> dict:
    try:
        usage = psutil.cpu_percent(interval=1)
        return {"status": "ok", "cpu": usage}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def ram_usage() -> dict:
    try:
        mem = psutil.virtual_memory()
        return {"status": "ok", "ram": mem.percent}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def disk_usage() -> dict:
    try:
        disk = psutil.disk_usage('/')
        return {"status": "ok", "disk": disk.percent}
    except Exception as e:
        return {"status": "error", "message": str(e)} 