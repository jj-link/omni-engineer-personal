"""CBORG provider implementation."""

import os
from typing import List, Dict, Any, Optional
from ..config import Configuration
from ..response import make_request, ResponseError

async def list_models() -> List[Dict[str, str]]:
    """List available CBORG models."""
    api_key = os.getenv("CBORG_API_KEY")
    if not api_key:
        raise ResponseError("CBORG API key not found", provider="cborg")
        
    response = await make_request(
        "GET",
        "https://api.cborg.lbl.gov/models",
        provider="cborg",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    # The response has a 'data' field containing the list of models
    models = response.get('data', [])
    
    print("\nAvailable CBORG Models:")
    print("----------------------")
    for model in models:
        print(f"ID: {model.get('id', 'N/A')}")
        print(f"Object Type: {model.get('object', 'N/A')}")
        print(f"Created: {model.get('created', 'N/A')}")
        print(f"Owned By: {model.get('owned_by', 'N/A')}")
        print("----------------------")
    
    return models

async def chat_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    **kwargs
) -> Dict[str, Any]:
    """Send a chat completion request to CBORG."""
    config = Configuration()
    api_key = os.getenv("CBORG_API_KEY")
    if not api_key:
        raise ResponseError("CBORG API key not found", provider="cborg")
    
    # Use default model if none specified
    if not model:
        model = config.model
    
    # Build request payload
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    # Add optional parameters if specified
    if temperature is not None:
        payload["temperature"] = temperature
    if top_p is not None:
        payload["top_p"] = top_p
    
    # Add any additional parameters
    payload.update(kwargs)
    
    response = await make_request(
        "POST",
        "https://api.cborg.lbl.gov/v1/chat/completions",
        provider="cborg",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload
    )
    
    return response
