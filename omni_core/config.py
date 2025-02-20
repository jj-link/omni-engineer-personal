"""Configuration module for Omni Engineer."""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Configuration:
    """Configuration class for Omni Engineer."""
    
    def __init__(self):
        """Initialize configuration."""
        self.provider: str = "ollama"
        self.model: str = "llama2"
        self.temperature: float = 0.7
        self.top_p: float = 0.95
        self.max_tokens: Optional[int] = None
        self.seed: Optional[int] = None
    
    def update_provider(self, provider: str) -> None:
        """Update provider configuration."""
        self.provider = provider
    
    def update_model(self, model: str) -> None:
        """Update model configuration."""
        self.model = model
    
    def update_parameters(self, parameters: dict) -> None:
        """Update model parameters."""
        if "temperature" in parameters:
            self.temperature = parameters["temperature"]
        if "top_p" in parameters:
            self.top_p = parameters["top_p"]
        if "max_tokens" in parameters:
            self.max_tokens = parameters["max_tokens"]
        if "seed" in parameters:
            self.seed = parameters["seed"]
