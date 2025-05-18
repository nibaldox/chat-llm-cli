import openai
import os
from chat_cli.config import get_api_key as config_get_api_key, get_default_model as config_get_default_model

class OpenAIProvider:
    def __init__(self, api_key: str = None, model: str = None):
        # Determine API Key
        _api_key = api_key  # API key passed to constructor takes precedence
        if not _api_key:
            _api_key = config_get_api_key('openai') # Try config file
        if not _api_key:
            _api_key = os.getenv('OPENAI_API_KEY') # Try environment variable
        
        self.api_key = _api_key # Store resolved API key (can be None)
        if self.api_key:
            openai.api_key = self.api_key # Set it globally for the openai library if found
        # If self.api_key is None, the openai library will try its own methods 
        # (like checking env var OPENAI_API_KEY) or raise an AuthenticationError upon use.

        # Determine Model
        _model = model  # Model passed to constructor takes precedence
        if not _model:
            _model = config_get_default_model('openai') # Try config file
        if not _model: # If still None (e.g. user provided None and config is None or empty)
            _model = "gpt-3.5-turbo" # Default fallback

        self.model = _model

    def send_message(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI] Error: {e}"

    def stream_message(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            for chunk in response:
                if 'choices' in chunk and chunk.choices and 'delta' in chunk.choices[0]:
                    content = chunk.choices[0].delta.get('content')
                    if content:
                        yield content
        except Exception as e:
            yield f"[OpenAI] Error: {e}"
