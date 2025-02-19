"""Configuration module for Omni Engineer."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

# Provider configurations
PROVIDERS = {
    'cborg': {
        'env_key': 'CBORG_API_KEY',
        'base_url': 'https://api.cborg.lbl.gov',
        'default_model': 'lbl/cborg-coder:latest',
        'requires_key': True
    },
    'ollama': {
        'env_key': None,
        'base_url': 'http://localhost:11434',
        'default_model': 'codellama',
        'requires_key': False
    }
}

@dataclass
class ProviderParameters:
    """Model parameters configuration."""
    temperature: float = 0.7
    top_p: float = 0.9
    seed: Optional[int] = None
    max_tokens: Optional[int] = None

@dataclass
class ProviderConfig:
    """Provider-specific configuration."""
    name: str
    model: str
    base_url: str
    api_key: Optional[str] = None
    parameters: ProviderParameters = field(default_factory=ProviderParameters)

    def get_provider_url(self, endpoint: str) -> str:
        """Get provider-specific endpoint URL.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full URL for the endpoint
        """
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

class Configuration:
    """Global configuration singleton."""
    _instance = None
    _provider_config: Optional[ProviderConfig] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance

    @property
    def provider_config(self) -> ProviderConfig:
        """Get current provider configuration."""
        if self._provider_config is None:
            raise ValueError("Provider configuration not initialized")
        return self._provider_config

    def update_provider(self, provider_name: str) -> None:
        """Update provider configuration."""
        if provider_name not in PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider_name}")

        provider = PROVIDERS[provider_name]
        api_key = None

        if provider['requires_key']:
            api_key = os.getenv(provider['env_key'])
            if not api_key:
                raise ValueError(
                    f"API key not found. Set {provider['env_key']} environment variable."
                )

        self._provider_config = ProviderConfig(
            name=provider_name,
            model=provider['default_model'],
            base_url=provider['base_url'],
            api_key=api_key
        )

    def update_model(self, model_name: str) -> None:
        """Update model configuration."""
        if self._provider_config is None:
            raise ValueError("Provider not configured")
        self._provider_config.model = model_name

    def update_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update model parameters."""
        if self._provider_config is None:
            raise ValueError("Provider not configured")
        
        current_params = self._provider_config.parameters
        for key, value in parameters.items():
            if hasattr(current_params, key):
                setattr(current_params, key, value)
            else:
                raise ValueError(f"Invalid parameter: {key}")

    def get_provider_url(self, endpoint: str) -> str:
        """Get full URL for provider endpoint."""
        if self._provider_config is None:
            raise ValueError("Provider not configured")
        
        return self._provider_config.get_provider_url(endpoint)
