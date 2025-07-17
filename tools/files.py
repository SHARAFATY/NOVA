import os

def search_files(directory, pattern) -> dict:
    matches = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            if pattern in name:
                matches.append(os.path.join(root, name))
    return {"status": "ok", "matches": matches}

def read_file(path) -> dict:
    try:
        with open(path, 'r') as f:
            content = f.read()
        return {"status": "ok", "content": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def delete_file(path) -> dict:
    try:
        os.remove(path)
        return {"status": "ok", "message": f"Deleted {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_file(path, content="") -> dict:
    try:
        with open(path, 'w') as f:
            f.write(content)
        return {"status": "ok", "message": f"Created {path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)} 