import os
import tempfile
from chat_cli import history

def test_save_and_load_history():
    data = []
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        fname = tmp.name
    try:
        history.save_history(data, fname)
        loaded = history.load_history(fname)
        assert loaded == data
    finally:
        os.remove(fname)

def test_add_message():
    h = []
    history.add_message(h, 'user', 'hola')
    assert h[0]['role'] == 'user'
    assert h[0]['content'] == 'hola'
    assert 'timestamp' in h[0]

def test_clear_history():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        fname = tmp.name
    try:
        history.save_history([{'role': 'user', 'content': 'x', 'timestamp': 't'}], fname)
        history.clear_history(fname)
        loaded = history.load_history(fname)
        assert loaded == []
    finally:
        os.remove(fname)

def test_export_history_txt():
    h = [
        {'role': 'user', 'content': 'hola', 'timestamp': '2025-05-02T08:00:00'},
        {'role': 'bot', 'content': 'respuesta', 'timestamp': '2025-05-02T08:01:00'}
    ]
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        fname = tmp.name
    try:
        history.export_history_txt(h, fname)
        with open(fname) as f:
            lines = f.readlines()
        assert '[2025-05-02T08:00:00] user: hola' in lines[0]
        assert '[2025-05-02T08:01:00] bot: respuesta' in lines[1]
    finally:
        os.remove(fname)
