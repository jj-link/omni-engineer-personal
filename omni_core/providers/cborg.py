"""CBORG provider implementation."""

import os
from typing import List, Dict, Any, Optional
from ..config import Configuration
from ..response import make_request, ResponseError

# Model metadata with descriptions and capabilities
MODEL_METADATA = {
    # LBL Models
    'lbl/cborg-chat:latest': {
        'description': 'Berkeley Lab-hosted chat model based on Llama 3.3 70B + Vision',
        'capabilities': ['chat', 'vision']
    },
    'lbl/cborg-coder:latest': {
        'description': 'Berkeley Lab-hosted chat model for code assistance based on Qwen Coder 2.5',
        'capabilities': ['chat', 'code']
    },
    'lbl/cborg-vision:latest': {
        'description': 'Lab-hosted multi-modal model for image analysis Qwen 72B Vision',
        'capabilities': ['vision', 'chat']
    },
    'lbl/cborg-deepthought:latest': {
        'description': 'Lab-hosted deep reasoning model based on DeepSeekR1-Distill Llama 70B (experimental)',
        'capabilities': ['chat', 'reasoning']
    },
    
    # OpenAI Models
    'openai/chatgpt-4o': {
        'description': 'The latest high-quality multi-modal model from OpenAI for chat, coding and more',
        'capabilities': ['chat', 'code', 'vision']
    },
    'openai/chatgpt-4o-mini': {
        'description': 'Lightweight, low-cost multi-modal model from OpenAI for chat and vision',
        'capabilities': ['chat', 'vision']
    },
    'openai/o1': {
        'description': 'Latest release of deep reasoning model from OpenAI for chat, coding and analysis',
        'capabilities': ['chat', 'code', 'reasoning']
    },
    'openai/o1-mini': {
        'description': 'Lightweight reasoning model from OpenAI for chat, coding and analysis',
        'capabilities': ['chat', 'code', 'reasoning']
    },
    'openai/o3-mini': {
        'description': 'Latest lightweight reasoning model from OpenAI for chat, coding and analysis',
        'capabilities': ['chat', 'code', 'reasoning']
    },
    
    # Google Models
    'google/gemini-flash': {
        'description': 'Lightweight model with vision, optimized for speed and efficiency',
        'capabilities': ['chat', 'vision', 'fast']
    },
    'google/gemini-pro': {
        'description': 'Advanced model for general performance across a wide range of tasks',
        'capabilities': ['chat', 'general']
    },
    
    # Anthropic Models
    'anthropic/claude-haiku': {
        'description': 'Fast and affordable model, including vision capabilities',
        'capabilities': ['chat', 'vision', 'fast']
    },
    'anthropic/claude-sonnet:v2': {
        'description': 'Latest version of cost-optimized model with excellent reasoning and coding capabilities',
        'capabilities': ['chat', 'code', 'reasoning']
    },
    'anthropic/claude-opus': {
        'description': 'Advanced model for nuanced reasoning, math, coding and more',
        'capabilities': ['chat', 'code', 'math', 'reasoning']
    },
    
    # Other Models
    'wolfram/alpha': {
        'description': 'Knowledge base query source',
        'capabilities': ['knowledge']
    }
}

# Default capabilities for models without explicit metadata
DEFAULT_CAPABILITIES = {
    'chat': ['chat'],  # Models with :chat suffix
    'coder': ['code', 'chat'],  # Models with 'coder' in name
    'vision': ['vision', 'chat'],  # Models with 'vision' in name
    'default': ['chat']  # Default for unknown models
}

def get_model_metadata(model_id: str) -> Dict[str, Any]:
    """Get metadata for a model, including description and capabilities."""
    # Return known metadata if available
    if model_id in MODEL_METADATA:
        return MODEL_METADATA[model_id]
    
    # Infer capabilities for unknown models
    capabilities = []
    if ':chat' in model_id:
        capabilities.extend(DEFAULT_CAPABILITIES['chat'])
    if 'coder' in model_id.lower():
        capabilities.extend(DEFAULT_CAPABILITIES['coder'])
    if 'vision' in model_id.lower():
        capabilities.extend(DEFAULT_CAPABILITIES['vision'])
    if not capabilities:
        capabilities = DEFAULT_CAPABILITIES['default']
    
    # Remove duplicates while preserving order
    capabilities = list(dict.fromkeys(capabilities))
    
    return {
        'description': f'A model provided by {model_id.split("/")[0]}',
        'capabilities': capabilities
    }

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
    
    print("\nAvailable CBORG Models (Full Details):")
    print("----------------------")
    for model in models:
        print(f"Full model data: {model}")
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
