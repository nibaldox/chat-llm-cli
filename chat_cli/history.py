import json
import os
from datetime import datetime

def save_history(history, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def add_message(history, role, content):
    history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

def clear_history(filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([], f)

def export_history_txt(history, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for msg in history:
            f.write(f"[{msg['timestamp']}] {msg['role']}: {msg['content']}\n")
