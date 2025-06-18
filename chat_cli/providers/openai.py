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
        self.client = None # Initialize client as None
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            # Attempt to initialize without explicit API key, relying on environment variables
            # or other OpenAI library mechanisms.
            try:
                self.client = openai.OpenAI()
            except openai.AuthenticationError:
                 # If this fails, self.client remains None. send_message/stream_message will fail later.
                 # list_models will return an empty list.
                 pass


    def list_models(self):
        if not self.client:
            return [] # No client, no models
        try:
            models = self.client.models.list()
            filtered_models = []
            # Prioritized models
            priority_models = ["gpt-4o", "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-3.5-turbo"]

            # Add prioritized models first if they exist
            for model_id in priority_models:
                if any(m.id == model_id for m in models.data):
                    filtered_models.append(model_id)

            # Add other gpt models, excluding vision/image and already added ones
            for model in models.data:
                if model.id.startswith("gpt-") and \
                   "vision" not in model.id.lower() and \
                   "image" not in model.id.lower() and \
                   model.id not in filtered_models:
                    filtered_models.append(model.id)

            # Fallback: if no specific gpt models found after filtering, return some common ones
            # This is a safety net, might not be strictly necessary if API always returns good data
            if not filtered_models:
                 # Check if any gpt models were returned at all before filtering
                all_gpt_models = [m.id for m in models.data if m.id.startswith("gpt-")]
                if all_gpt_models:
                    return all_gpt_models[:5] # return first 5 gpt models if filters resulted in empty
                # else, if no gpt models at all, return the hardcoded list as a last resort
                return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]


            return filtered_models
        except openai.APIError as e:
            # print(f"[OpenAI Provider] API Error listing models: {e}") # Optional: log error
            return [] # Return empty list on API error
        except Exception as e:
            # print(f"[OpenAI Provider] Unexpected error listing models: {e}") # Optional: log error
            return []


    def send_message(self, prompt):
        if not self.client:
            return "[OpenAI] Error: Client not initialized. API key might be missing or invalid."
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except openai.APIError as e: # More specific error handling
            return f"[OpenAI] API Error: {e}"
        except Exception as e: # Catch-all for other issues
            return f"[OpenAI] Error: {e}"

    def stream_message(self, prompt):
        if not self.client:
            yield "[OpenAI] Error: Client not initialized. API key might be missing or invalid."
            return
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except openai.APIError as e: # More specific error handling
            yield f"[OpenAI] API Error: {e}"
        except Exception as e: # Catch-all for other issues
            yield f"[OpenAI] Error: {e}"
