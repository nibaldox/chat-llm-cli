from .openai import *
from .ollama import *
from .gemini import *
from .anthropic import *

def get_provider_names():
    return ["openai", "ollama", "gemini", "anthropic"]
