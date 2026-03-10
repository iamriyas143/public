import ollama
from .config import SYSTEM_PROMPT

class MistralEngine:
    def __init__(self):
        # Matches your 'ollama list' output
        self.model_name = "mistral:latest" 

    def generate_response(self, user_input):
        # The core logic: combining the hidden system prompt with user input
        response = ollama.chat(model=self.model_name, messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_input},
        ])
        return response['message']['content']

engine = MistralEngine()
