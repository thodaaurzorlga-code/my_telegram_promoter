from abc import ABC, abstractmethod
from google import genai
from groq import Groq


class LLMProvider(ABC):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def generate_response(self, prompt: str):
        pass


# ===================== Gemini (latest SDK) =====================
class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)
        self.client = genai.Client(api_key=api_key)

    def generate_response(self, prompt: str):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text


# ===================== Groq =====================
class GroqLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)
        self.client = Groq(api_key=api_key)

    def generate_response(self, prompt: str):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        
        # Ensure we're returning text, not a score or number
        if content is None:
            return ""
        
        content_str = str(content).strip()
        
        # If it's just a float/number (logit score), something went wrong
        try:
            float(content_str)
            # If this succeeds, we got a numeric response instead of text
            raise ValueError(f"Groq returned numeric response instead of text: {content_str}")
        except ValueError as e:
            if "could not convert" not in str(e).lower():
                # Re-raise if it's our error, not a float conversion error
                raise
        
        return content_str


# ===================== Registry =====================
class ProviderRegistry:
    _registry = {}

    @classmethod
    def register(cls, name: str, provider_cls):
        cls._registry[name.lower()] = provider_cls

    @classmethod
    def get(cls, name: str):
        if name.lower() not in cls._registry:
            raise ValueError(f"Provider {name} not registered.")
        return cls._registry[name.lower()]
