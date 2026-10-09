import os
from abc import ABC, abstractmethod
import google.generativeai as genai
from openai import OpenAI
import json
from pydantic import BaseModel

class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_instruction: str = "", response_format: type[BaseModel] = None) -> str:
        pass

class GeminiClient(LLMClient):
    def __init__(self, model_name="gemini-2.5-flash", api_key=None):
        genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(model_name)
        
    def generate(self, prompt: str, system_instruction: str = "", response_format: type[BaseModel] = None) -> str:
        try:
            # Fake/mock response for testing if no real key
            key = os.getenv("GEMINI_API_KEY", "your-gemini-key-here")
            if key == "your-gemini-key-here":
                if response_format:
                    return "{}"
                return "Mocked LLM Response"
                
            contents = []
            if system_instruction:
                contents.append({"role": "user", "parts": [f"System: {system_instruction}"]})
                contents.append({"role": "model", "parts": ["Understood."]})
            contents.append({"role": "user", "parts": [prompt]})
            
            response = self.model.generate_content(contents)
            return response.text
        except Exception as e:
            print(f"Gemini error: {e}")
            if response_format: return "{}"
            return "Error from Gemini"

class OpenAIClient(LLMClient):
    def __init__(self, model_name="gpt-4o-mini", api_key=None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY", "your-openai-key-here"))
        self.model_name = model_name
        
    def generate(self, prompt: str, system_instruction: str = "", response_format: type[BaseModel] = None) -> str:
        try:
            if self.client.api_key == "your-openai-key-here":
                if response_format: return "{}"
                return "Mocked LLM Response"
                
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            # Simple implementation without strict schema enforcement for now
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {e}")
            if response_format: return "{}"
            return "Error from OpenAI"

from groq import Groq

class GroqClient(LLMClient):
    def __init__(self, model_name="openai/gpt-oss-120b", api_key=None):
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY", "your-groq-key-here"))
        self.model_name = model_name
        
    def generate(self, prompt: str, system_instruction: str = "", response_format: type[BaseModel] = None) -> str:
        try:
            if self.client.api_key == "your-groq-key-here":
                if response_format: return "{}"
                return "Mocked LLM Response"
                
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=1,
                max_completion_tokens=2048,
                top_p=1,
                reasoning_effort="medium",
                stream=True,
                stop=None
            )
            
            result = ""
            for chunk in completion:
                result += chunk.choices[0].delta.content or ""
            return result
        except Exception as e:
            print(f"Groq error: {e}")
            if response_format: return "{}"
            return "Error from Groq"

def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "groq")
    if provider == "openai":
        return OpenAIClient(os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    elif provider == "groq":
        return GroqClient()
    else:
        return GeminiClient(os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
