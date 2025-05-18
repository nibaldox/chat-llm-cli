import yaml
import os
from pathlib import Path

CONFIG_FILE_NAME = "config.yaml"
# Por ahora, buscaremos el config.yaml en la raíz del proyecto.
# Más adelante, podríamos buscar en ~/.config/chat_cli/config.yaml
CONFIG_FILE_PATH = Path(__file__).resolve().parent.parent / CONFIG_FILE_NAME

_config = None

def load_config():
    """
    Carga la configuración desde el archivo config.yaml si existe.
    Retorna un diccionario con la configuración o None si el archivo no existe.
    """
    global _config
    if _config is not None: # Ya cargado
        return _config

    if CONFIG_FILE_PATH.exists():
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                _config = yaml.safe_load(f)
            if _config is None: # Archivo vacío o YAML inválido que resulta en None
                _config = {}
            return _config
        except yaml.YAMLError as e:
            print(f"Error al parsear {CONFIG_FILE_NAME}: {e}")
            _config = {} # Tratar como si no hubiera config válida
            return _config
        except Exception as e:
            print(f"Error al leer {CONFIG_FILE_NAME}: {e}")
            _config = {}
            return _config
    _config = {} # Archivo no encontrado
    return _config

def get_provider_config(provider_name: str):
    """
    Obtiene la configuración específica para un proveedor.
    Ej: get_provider_config("openai") -> {"api_key": "sk-...", "default_model": "gpt-3.5-turbo"}
    """
    config = load_config()
    return config.get("providers", {}).get(provider_name, {})

def get_api_key(provider_name: str):
    """
    Obtiene la API key para un proveedor desde config.yaml.
    Retorna None si no se encuentra.
    """
    provider_conf = get_provider_config(provider_name)
    return provider_conf.get("api_key")

def get_default_model(provider_name: str):
    """
    Obtiene el modelo por defecto para un proveedor desde config.yaml.
    Retorna None si no se encuentra.
    """
    provider_conf = get_provider_config(provider_name)
    return provider_conf.get("default_model")

if __name__ == '__main__':
    # Para pruebas rápidas
    load_config()
    print(f"Configuración cargada: {_config}")
    print(f"OpenAI API Key desde config: {get_api_key('openai')}")
    print(f"OpenAI Default Model desde config: {get_default_model('openai')}")
    print(f"Anthropic API Key desde config: {get_api_key('anthropic')}")
    print(f"Gemini API Key desde config: {get_api_key('gemini')}")
    print(f"Proveedor inexistente: {get_provider_config('noexiste')}")
