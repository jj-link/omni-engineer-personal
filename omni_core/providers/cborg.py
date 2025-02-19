"""CBORG provider implementation."""

import json
import aiohttp
from typing import Dict, Any, Optional, List
from ..config import Configuration
from ..response import make_request, validate_json_response

async def list_models() -> List[Dict[str, Any]]:
    """List available CBORG models.
    
    Returns:
        List of model information dictionaries
    """
    config = Configuration().provider_config
    url = config.get_provider_url("models")
    
    response = await make_request(
        "GET",
        url,
        provider="cborg",
        headers={"Authorization": f"Bearer {config.api_key}"}
    )
    return response["models"]

async def chat_completion(
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_tokens: Optional[int] = None,
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """Generate chat completion using CBORG.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        temperature: Sampling temperature (0-1)
        top_p: Nucleus sampling parameter (0-1)
        max_tokens: Maximum tokens in response
        seed: Random seed for reproducibility
        
    Returns:
        Response from CBORG API
    """
    config = Configuration().provider_config
    url = config.get_provider_url("chat/completions")
    
    # Build request payload
    payload = {
        "model": config.model,
        "messages": messages,
        "stream": False
    }
    
    # Add optional parameters if specified
    if temperature is not None:
        payload["temperature"] = temperature
    if top_p is not None:
        payload["top_p"] = top_p
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if seed is not None:
        payload["seed"] = seed
    
    return await make_request(
        "POST",
        url,
        provider="cborg",
        json=payload,
        headers={"Authorization": f"Bearer {config.api_key}"}
    )
