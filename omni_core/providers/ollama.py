"""Ollama provider implementation for the Omni Engineer."""
import json
from typing import Dict, List, Optional
import aiohttp
from ..config import ProviderConfig

class OllamaProvider:
    """Provider implementation for Ollama local models."""
    
    def __init__(self, config: ProviderConfig):
        """Initialize the Ollama provider with configuration."""
        self.config = config
        self.base_url = config.base_url or "http://localhost:11434"
        
    async def list_models(self) -> List[str]:
        """List available models from Ollama."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status != 200:
                    raise Exception(f"Failed to list models: {response.status}")
                data = await response.json()
                return [model['name'] for model in data['models']]

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
    ) -> Dict:
        """Generate chat completion using Ollama.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Name of the Ollama model to use
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
            stop: List of strings that will stop generation if encountered
            
        Returns:
            Dictionary containing the completion response
        """
        # Build request payload
        payload = {
            "model": model,
            "messages": messages,  # Ollama supports ChatML format directly
            "options": {
                "temperature": temperature if temperature is not None else 0.7,
                "top_p": top_p if top_p is not None else 1.0,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
            
        if stop:
            payload["options"]["stop"] = stop

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Chat completion failed: {error_text}")
                
                data = await response.json()
                
                # Format response to match our expected structure
                return {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": data["message"]["content"]
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                        "total_tokens": (
                            data.get("prompt_eval_count", 0) + 
                            data.get("eval_count", 0)
                        )
                    }
                }