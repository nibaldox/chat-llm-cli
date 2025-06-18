# Integración inicial para Gemini
# NOTA: Sustituir la lógica de ejemplo por la integración real con la API de Gemini de Google
import os
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from google.auth import exceptions as auth_exceptions # Import for specific auth errors
from chat_cli.config import get_api_key as config_get_api_key, get_default_model as config_get_default_model

class GeminiProvider:
    def __init__(self, api_key: str = None, model: str = None):
        _resolved_api_key = api_key
        if not _resolved_api_key:
            _resolved_api_key = config_get_api_key('gemini')
        if not _resolved_api_key:
            _resolved_api_key = os.getenv('GEMINI_API_KEY')

        self.api_key = _resolved_api_key

        _resolved_model = model
        if not _resolved_model:
            _resolved_model = config_get_default_model('gemini')
        if not _resolved_model and "GEMINI_DEFAULT_MODEL" in os.environ: # Check env for default model
            _resolved_model = os.environ["GEMINI_DEFAULT_MODEL"]
        if not _resolved_model: # Fallback to a common default if still not found
            _resolved_model = "gemini-pro"
        
        self.model = _resolved_model

        if not self.api_key:
            raise ValueError("Gemini API key is missing. Please set it in the config, as an environment variable (GEMINI_API_KEY), or pass it directly.")

        try:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        except auth_exceptions.DefaultCredentialsError as e:
            raise ValueError(f"Gemini API key is invalid or not configured properly: {e}")
        except Exception as e: # Catch other potential configuration errors
            raise ValueError(f"Failed to initialize Gemini client (model: {self.model}): {e}")

    def send_message(self, prompt):
        try:
            response = self.client.generate_content(prompt)
            return response.text
        except google_exceptions.GoogleAPIError as e:
            return f"[Gemini API Error]: {e}"
        except Exception as e: # Catch other unexpected errors
            return f"[Gemini Error]: An unexpected error occurred: {e}"

    def stream_message(self, prompt):
        try:
            response = self.client.generate_content(prompt, stream=True)
            for chunk in response:
                yield chunk.text
        except google_exceptions.GoogleAPIError as e:
            yield f"[Gemini API Error]: {e}"
        except Exception as e: # Catch other unexpected errors
            yield f"[Gemini Error]: An unexpected error occurred during streaming: {e}"
