"""
Client implementations for different model providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union
import requests
from urllib.parse import urlparse

from .config import APIConfig

@dataclass
class ModelParameters:
    """Parameters for model generation."""
    temperature: float = 0.7
    top_p: float = 1.0
    seed: Optional[int] = None
    model: Optional[str] = None

class ModelClient(ABC):
    """Abstract base class for model clients."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self._validate_url(base_url)
    
    @abstractmethod
    def generate(self, prompt: str, params: ModelParameters) -> str:
        """Generate text from the model."""
        pass
    
    @abstractmethod
    def stream(self, prompt: str, params: ModelParameters) -> str:
        """Stream text from the model."""
        pass
    
    def _validate_url(self, url: str) -> None:
        """Validate URL format."""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError(f"Invalid URL format: {url}")
        except Exception as e:
            raise ValueError(f"Invalid URL: {url}") from e

class CBORGClient(ModelClient):
    """Client for CBORG API."""
    
    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url, api_key)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate(self, prompt: str, params: ModelParameters) -> str:
        """Generate text from CBORG model."""
        data = {
            "model": params.model or APIConfig.PROVIDERS['cborg']['default_model'],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.temperature,
            "top_p": params.top_p
        }
        if params.seed is not None:
            data["seed"] = params.seed
            
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    
    def stream(self, prompt: str, params: ModelParameters) -> str:
        """Stream text from CBORG model."""
        data = {
            "model": params.model or APIConfig.PROVIDERS['cborg']['default_model'],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": params.temperature,
            "top_p": params.top_p,
            "stream": True
        }
        if params.seed is not None:
            data["seed"] = params.seed
            
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers=self.headers,
            json=data,
            stream=True
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                # Process SSE data
                yield line.decode('utf-8')

class OllamaClient(ModelClient):
    """Client for Ollama API."""
    
    def generate(self, prompt: str, params: ModelParameters) -> str:
        """Generate text from Ollama model."""
        data = {
            "model": params.model or APIConfig.PROVIDERS['ollama']['default_model'],
            "prompt": prompt,
            "options": {
                "temperature": params.temperature,
                "top_p": params.top_p
            }
        }
        if params.seed is not None:
            data["options"]["seed"] = params.seed
            
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=data
        )
        response.raise_for_status()
        return response.json()["response"]
    
    def stream(self, prompt: str, params: ModelParameters) -> str:
        """Stream text from Ollama model."""
        data = {
            "model": params.model or APIConfig.PROVIDERS['ollama']['default_model'],
            "prompt": prompt,
            "options": {
                "temperature": params.temperature,
                "top_p": params.top_p
            },
            "stream": True
        }
        if params.seed is not None:
            data["options"]["seed"] = params.seed
            
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=data,
            stream=True
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                yield line.decode('utf-8')

class ClientFactory:
    """Factory for creating model clients."""
    
    @staticmethod
    def create_client(provider: str, args: Any) -> ModelClient:
        """Create a client for the specified provider."""
        config = APIConfig.get_config(provider)
        
        if provider == 'cborg':
            api_key = APIConfig.get_api_key(provider)
            return CBORGClient(config['base_url'], api_key)
        elif provider == 'ollama':
            base_url = getattr(args, 'ollama_url', config['base_url'])
            return OllamaClient(base_url)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
