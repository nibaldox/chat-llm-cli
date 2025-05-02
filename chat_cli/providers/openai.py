import openai

class OpenAIProvider:
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        self.api_key = api_key or "API_KEY_AQUI"
        self.model = model
        openai.api_key = self.api_key

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
