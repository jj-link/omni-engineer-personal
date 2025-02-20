"""Configuration management for the omni-engineer."""

import os
from typing import Optional, Dict, Any, List

class Configuration:
    """Configuration class for managing provider settings."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize configuration with default values."""
        self._provider = "cborg"  # Default provider
        self._model = "lbl/cborg-coder:chat"  # Default model
        self._temperature = 0.7
        self._top_p = 1.0
        
        # Provider-specific configurations
        self._providers = {
            "cborg": {
                "api_key": os.getenv("CBORG_API_KEY"),
                "models": ["lbl/cborg-coder:chat"],
                "default_model": "lbl/cborg-coder:chat"
            }
        }
    
    @property
    def provider(self) -> str:
        """Get current provider."""
        return self._provider
    
    @property
    def model(self) -> str:
        """Get current model."""
        return self._model
    
    @property
    def temperature(self) -> float:
        """Get temperature setting."""
        return self._temperature
    
    @property
    def top_p(self) -> float:
        """Get top_p setting."""
        return self._top_p
    
    def update_provider(self, provider: str) -> None:
        """Update current provider."""
        if provider not in self._providers:
            raise ValueError(f"Unsupported provider: {provider}")
        self._provider = provider
        self._model = self._providers[provider]["default_model"]
    
    def update_model(self, model: str) -> None:
        """Update current model."""
        if model not in self._providers[self._provider]["models"]:
            raise ValueError(f"Unsupported model for provider {self._provider}: {model}")
        self._model = model
    
    def update_temperature(self, temperature: float) -> None:
        """Update temperature setting."""
        if not 0 <= temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        self._temperature = temperature
    
    def update_top_p(self, top_p: float) -> None:
        """Update top_p setting."""
        if not 0 <= top_p <= 1:
            raise ValueError("Top_p must be between 0 and 1")
        self._top_p = top_p
    
    def list_models(self) -> List[Dict[str, str]]:
        """List available models for current provider."""
        models = self._providers[self._provider]["models"]
        return [{"id": model, "name": model, "description": ""} for model in models]
    
    def get_api_key(self) -> Optional[str]:
        """Get API key for current provider."""
        return self._providers[self._provider]["api_key"]
