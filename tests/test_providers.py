from chat_cli.providers.openai import OpenAIProvider
from chat_cli.providers.ollama import OllamaProvider
from chat_cli.providers.gemini import GeminiProvider
import types

def test_openai_send_message(monkeypatch):
    provider = OpenAIProvider(api_key="test", model="gpt-3.5-turbo")
    def fake_create(**kwargs):
        class Choice:
            def __init__(self):
                self.message = types.SimpleNamespace(content="respuesta openai")
        return types.SimpleNamespace(choices=[Choice()])
    monkeypatch.setattr("openai.ChatCompletion.create", fake_create)
    assert provider.send_message("hola") == "respuesta openai"

def test_ollama_send_message(monkeypatch):
    provider = OllamaProvider(model="llama2")
    monkeypatch.setattr(provider, "send_message", lambda prompt: "respuesta ollama")
    assert provider.send_message("hola") == "respuesta ollama"

def test_gemini_send_message():
    provider = GeminiProvider()
    assert "simulada" in provider.send_message("hola")
