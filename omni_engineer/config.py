"""
Configuration management for the Omni Engineer multi-model system.
"""
import os
from typing import Optional, Dict, Any

class APIConfig:
    """Configuration management for different API providers."""
    
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

    @classmethod
    def get_config(cls, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider."""
        if provider not in cls.PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        return cls.PROVIDERS[provider]

    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """Get API key for a specific provider if required."""
        config = cls.get_config(provider)
        if not config['requires_key']:
            return None
            
        env_key = config['env_key']
        api_key = os.getenv(env_key)
        
        if not api_key:
            raise ValueError(f"Missing {env_key} environment variable")
            
        return api_key
