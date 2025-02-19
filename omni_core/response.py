"""Response handling module for Omni Engineer.

This module handles response validation, format checking, and automatic retries.
"""

import json
import asyncio
import logging
from typing import Any, Dict, Optional, TypeVar, Callable, Awaitable
from dataclasses import dataclass
from functools import wraps
import aiohttp
from rich.console import Console

from .errors import ResponseError, ConnectionError

console = Console()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_retries: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 8.0  # seconds
    backoff_factor: float = 2.0
    retry_on_status: tuple = (408, 429, 500, 502, 503, 504)

T = TypeVar('T')

def with_retries(retry_config: Optional[RetryConfig] = None) -> Callable:
    """Decorator for adding retry behavior to async functions.
    
    Args:
        retry_config: Optional retry configuration. Uses default if not provided.
    """
    if retry_config is None:
        retry_config = RetryConfig()

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            delay = retry_config.initial_delay

            for attempt in range(retry_config.max_retries):
                try:
                    return await func(*args, **kwargs)
                except aiohttp.ClientError as e:
                    last_exception = e
                    status = getattr(e, 'status', None)
                    
                    # Only retry on specific status codes
                    if status and status not in retry_config.retry_on_status:
                        raise
                    
                    if attempt < retry_config.max_retries - 1:
                        logger.warning(
                            f"Request failed (attempt {attempt + 1}/{retry_config.max_retries}): {str(e)}"
                        )
                        await asyncio.sleep(delay)
                        delay = min(delay * retry_config.backoff_factor, retry_config.max_delay)
                    
            raise last_exception or ConnectionError("Max retries exceeded")
            
        return wrapper
    return decorator

async def validate_json_response(response: aiohttp.ClientResponse) -> Dict[str, Any]:
    """Validate and parse a JSON response.
    
    Args:
        response: The aiohttp response to validate
        
    Returns:
        The parsed JSON response
        
    Raises:
        ResponseError: If the response is invalid
    """
    try:
        data = await response.json()
    except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
        text = await response.text()
        raise ResponseError(
            "Invalid JSON response",
            {
                "status": response.status,
                "content_type": response.content_type,
                "text": text[:200],  # First 200 chars for context
                "error": str(e)
            }
        )
    
    return data

def validate_ollama_response(data: Dict[str, Any]) -> None:
    """Validate Ollama response format.
    
    Args:
        data: The response data to validate
        
    Raises:
        ResponseError: If the response format is invalid
    """
    if not isinstance(data, dict):
        raise ResponseError(
            "Invalid Ollama response format",
            {"error": "Response must be a dictionary"}
        )
    
    # Validate response based on endpoint
    if "models" in data:
        # Response from /api/tags
        if not isinstance(data["models"], list):
            raise ResponseError(
                "Invalid Ollama models response",
                {"error": "models field must be a list"}
            )
        for model in data["models"]:
            if not isinstance(model, dict) or "name" not in model:
                raise ResponseError(
                    "Invalid Ollama model format",
                    {"error": "Each model must be a dictionary with a name field"}
                )
    
    elif "response" in data:
        # Response from chat endpoint
        if not isinstance(data["response"], str):
            raise ResponseError(
                "Invalid Ollama chat response",
                {"error": "response field must be a string"}
            )
    
    else:
        raise ResponseError(
            "Unknown Ollama response format",
            {"available_fields": list(data.keys())}
        )

def validate_cborg_response(data: Dict[str, Any]) -> None:
    """Validate CBORG response format.
    
    Args:
        data: The response data to validate
        
    Raises:
        ResponseError: If the response format is invalid
    """
    # Will be implemented when we add CBORG support
    pass

@with_retries()
async def make_request(
    method: str,
    url: str,
    provider: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """Make an HTTP request with retries and validation.
    
    Args:
        method: HTTP method to use
        url: URL to request
        provider: Provider name for response validation
        **kwargs: Additional arguments for aiohttp request
        
    Returns:
        The validated response data
        
    Raises:
        ConnectionError: If the request fails
        ResponseError: If the response is invalid
    """
    async with aiohttp.ClientSession() as session:
        async with await getattr(session, method.lower())(url, **kwargs) as response:
            if response.status != 200:
                raise ResponseError(
                    f"Request failed with status {response.status}",
                    {
                        "status": response.status,
                        "reason": response.reason,
                        "url": url
                    }
                )
            
            data = await validate_json_response(response)
            
            # Validate provider-specific response format
            if provider == "ollama":
                validate_ollama_response(data)
            elif provider == "cborg":
                validate_cborg_response(data)
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            return data
