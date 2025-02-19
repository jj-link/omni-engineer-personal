"""Configuration module for Omni Engineer.

This module handles provider configuration, environment variables, and validation.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ProviderParameters:
    """Common parameters across providers"""
    temperature: float = 0.7
    top_p: float = 0.9
    seed: Optional[int] = None

@dataclass
class ProviderConfig:
    """Configuration for a provider"""
    base_url: str
    default_model: str
    requires_key: bool
    parameters: ProviderParameters = field(default_factory=ProviderParameters)

class ConfigurationError(Exception):
    """Raised when there is a configuration error"""
    pass

class Configuration:
    """Main configuration class"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.providers: Dict[str, ProviderConfig] = {
            'cborg': ProviderConfig(
                base_url='https://api.cborg.lbl.gov',
                default_model='lbl/cborg-coder:latest',
                requires_key=True
            ),
            'ollama': ProviderConfig(
                base_url='http://localhost:11434',
                default_model='codellama',
                requires_key=False
            )
        }
        self._initialized = True

    def validate_environment(self) -> None:
        """Validate required environment variables are present"""
        # Check Tavily API key (always required)
        if not os.getenv('TAVILY_API_KEY'):
            raise ConfigurationError("TAVILY_API_KEY not found in environment variables")

        # Check provider-specific keys
        for name, provider in self.providers.items():
            if provider.requires_key:
                key_name = f"{name.upper()}_API_KEY"
                if not os.getenv(key_name):
                    raise ConfigurationError(f"{key_name} not found in environment variables")

    def get_provider(self, name: str) -> ProviderConfig:
        """Get provider configuration by name"""
        if name not in self.providers:
            raise ConfigurationError(f"Unknown provider: {name}")
        return self.providers[name]

    def update_provider_model(self, name: str, model: str) -> None:
        """Update the model for a provider"""
        if name not in self.providers:
            raise ConfigurationError(f"Unknown provider: {name}")
        self.providers[name].default_model = model

    def update_provider_parameters(self, name: str, **kwargs: Any) -> None:
        """Update parameters for a provider"""
        if name not in self.providers:
            raise ConfigurationError(f"Unknown provider: {name}")
        
        provider = self.providers[name]
        
        if 'temperature' in kwargs:
            temp = kwargs['temperature']
            if not 0.0 <= temp <= 1.0:
                raise ConfigurationError("Temperature must be between 0.0 and 1.0")
            provider.parameters.temperature = temp
            
        if 'top_p' in kwargs:
            top_p = kwargs['top_p']
            if not 0.0 <= top_p <= 1.0:
                raise ConfigurationError("Top-p must be between 0.0 and 1.0")
            provider.parameters.top_p = top_p
            
        if 'seed' in kwargs:
            provider.parameters.seed = kwargs['seed']

    def get_api_key(self, name: str) -> Optional[str]:
        """Get API key for a provider"""
        if name not in self.providers:
            raise ConfigurationError(f"Unknown provider: {name}")
        
        provider = self.providers[name]
        if not provider.requires_key:
            return None
            
        key_name = f"{name.upper()}_API_KEY"
        key = os.getenv(key_name)
        if not key:
            raise ConfigurationError(f"{key_name} not found in environment variables")
        return key
