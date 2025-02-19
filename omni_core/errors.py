"""Error handling module for Omni Engineer.

This module defines custom exceptions and error handling utilities.
"""

from typing import Optional, Dict, Any
import aiohttp
from rich.console import Console

console = Console()

class OmniError(Exception):
    """Base exception class for Omni Engineer."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class ConnectionError(OmniError):
    """Raised when there are network connectivity issues."""
    pass

class AuthenticationError(OmniError):
    """Raised when there are API key or authentication issues."""
    pass

class ModelError(OmniError):
    """Raised when there are issues with model availability or compatibility."""
    pass

class ConfigurationError(OmniError):
    """Raised when there are configuration issues."""
    pass

class ResponseError(OmniError):
    """Raised when there are issues with API responses."""
    pass

def format_error(error: OmniError) -> str:
    """Format an error message with details for display."""
    message = f"[red]Error:[/red] {error.message}"
    if error.details:
        details = "\n".join(f"  - {k}: {v}" for k, v in error.details.items())
        message += f"\nDetails:\n{details}"
    return message

async def check_connection(url: str) -> None:
    """Check if a URL is accessible.
    
    Args:
        url: The URL to check
        
    Raises:
        ConnectionError: If the URL is not accessible
    """
    session = aiohttp.ClientSession()
    try:
        async with session:
            async with await session.get(url) as response:
                if response.status != 200:
                    raise ConnectionError(
                        f"Failed to connect to {url}",
                        {"status": response.status, "reason": response.reason}
                    )
    except aiohttp.ClientError as e:
        raise ConnectionError(
            f"Failed to connect to {url}",
            {"error": str(e)}
        )
    finally:
        await session.close()

def validate_api_key(key: Optional[str], provider: str) -> None:
    """Validate that an API key is present and well-formed.
    
    Args:
        key: The API key to validate
        provider: The name of the provider requiring the key
        
    Raises:
        AuthenticationError: If the key is missing or malformed
    """
    if not key:
        raise AuthenticationError(
            f"Missing API key for {provider}",
            {"provider": provider}
        )
    
    # Add provider-specific key validation
    if provider == "cborg":
        if not key.startswith("cborg_"):
            raise AuthenticationError(
                f"Invalid API key format for {provider}",
                {"provider": provider, "expected_prefix": "cborg_"}
            )

async def check_model_availability(provider: str, model: str, base_url: str) -> None:
    """Check if a model is available for use.
    
    Args:
        provider: The provider name
        model: The model to check
        base_url: The base URL for the provider's API
        
    Raises:
        ModelError: If the model is not available
        ConnectionError: If there are connectivity issues
    """
    if provider == "ollama":
        session = aiohttp.ClientSession()
        try:
            async with session:
                async with await session.get(f"{base_url}/api/tags") as response:
                    if response.status != 200:
                        raise ModelError(
                            f"Failed to get model list from {provider}",
                            {"status": response.status, "reason": response.reason}
                        )
                    models = await response.json()
                    if not any(m["name"] == model for m in models["models"]):
                        raise ModelError(
                            f"Model {model} not available for {provider}",
                            {"available_models": [m["name"] for m in models["models"]]}
                        )
        except aiohttp.ClientError as e:
            raise ConnectionError(
                f"Failed to connect to {provider}",
                {"error": str(e)}
            )
        finally:
            await session.close()
    elif provider == "cborg":
        # CBORG model availability check will be implemented when we add CBORG support
        pass
    else:
        raise ConfigurationError(
            f"Unknown provider: {provider}",
            {"available_providers": ["ollama", "cborg"]}
        )
