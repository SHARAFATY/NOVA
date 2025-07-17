import psutil

def list_processes() -> dict:
    try:
        procs = [p.info for p in psutil.process_iter(['pid', 'name', 'username'])]
        return {"status": "ok", "processes": procs}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def kill_process(pid: int) -> dict:
    try:
        p = psutil.Process(pid)
        p.terminate()
        return {"status": "ok", "message": f"Process {pid} terminated."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def monitor_process(pid: int) -> dict:
    try:
        p = psutil.Process(pid)
        info = p.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_info'])
        return {"status": "ok", "info": info}
    except Exception as e:
        return {"status": "error", "message": str(e)} 