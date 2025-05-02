try:
    import ollama
except ImportError:
    ollama = None
import requests
import json

class OllamaProvider:
    def __init__(self, model="llama2"):
        self.model = model
        self.history = []

    def send_message(self, prompt):
        # Añadir el mensaje del usuario al historial
        self.history.append({"role": "user", "content": prompt})
        # Si la librería está instalada, usarla
        if ollama:
            try:
                response = ollama.chat(model=self.model, messages=self.history)
                content = response['message']['content']
                # Añadir respuesta al historial
                self.history.append({"role": "assistant", "content": content})
                return content
            except Exception as e:
                return f"[Ollama] Error: {e}"
        # Si no, intentar vía HTTP local
        try:
            url = "http://localhost:11434/api/chat"
            payload = {"model": self.model, "messages": self.history}
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # Extraer contenido de la respuesta
            if 'message' in data and isinstance(data['message'], dict):
                content = data['message'].get('content')
            elif 'choices' in data and isinstance(data['choices'], list) and data['choices']:
                choice = data['choices'][0]
                if 'message' in choice:
                    content = choice['message'].get('content')
                else:
                    content = choice.get('delta', {}).get('content')
            else:
                content = data.get('content')
            if not content:
                content = '[Ollama] Sin respuesta'
            # Añadir respuesta al historial
            self.history.append({"role": "assistant", "content": content})
            return content
        except Exception as e:
            return f"[Ollama] Error HTTP: {e}"

    def stream_message(self, prompt):
        # Añadir el mensaje del usuario al historial
        self.history.append({"role": "user", "content": prompt})
        url = "http://localhost:11434/api/chat"
        payload = {"model": self.model, "messages": self.history, "stream": True}
        full_response = ""
        try:
            with requests.post(url, json=payload, stream=True) as resp:
                resp.raise_for_status()
                for raw in resp.iter_lines(decode_unicode=False):
                    if not raw:
                        continue
                    # raw es bytes, decodificar manualmente
                    line_str = raw.decode("utf-8", errors="ignore").strip()
                    # Manejar prefijo SSE 'data:'
                    if line_str.startswith("data:"):
                        line_str = line_str[len("data:"):].strip()
                    if not line_str:
                        continue
                    try:
                        data = json.loads(line_str)
                    except json.JSONDecodeError:
                        continue
                    # Extraer contenido
                    content = None
                    choices = data.get("choices")
                    if choices and isinstance(choices, list):
                        choice = choices[0]
                        delta = choice.get("delta")
                        if isinstance(delta, dict) and "content" in delta:
                            content = delta["content"]
                        elif "message" in choice and "content" in choice["message"]:
                            content = choice["message"]["content"]
                    else:
                        content = data.get("content") or data.get("message", {}).get("content")
                    if content:
                        full_response += content
                        yield content
            # Añadir respuesta al historial si existe
            if full_response:
                self.history.append({"role": "assistant", "content": full_response})
        except Exception as e:
            yield f"[Ollama] Error HTTP streaming: {e}"
