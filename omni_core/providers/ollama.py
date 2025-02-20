"""Ollama provider implementation."""

import json
import sys
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from ..base import BaseProvider

class OllamaProvider(BaseProvider):
    """Provider implementation for Ollama local models."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Ollama provider.
        
        Args:
            base_url: Base URL for Ollama API
        """
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger(__name__)
    
    async def list_models(self) -> List[str]:
        """List available models.
        
        Returns:
            List of model names
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status != 200:
                        raise Exception(f"Failed to list models: {response.status}")
                    
                    data = await response.json()
                    return [model['name'] for model in data['models']]
                    
        except Exception as e:
            self.logger.error(f"Error listing models: {str(e)}")
            raise
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama2",
        temperature: float = 0.7,
        top_p: float = 0.95,
        seed: Optional[int] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send chat completion request.
        
        Args:
            messages: List of message dictionaries
            model: Model name to use
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            seed: Random seed
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Chat completion response
        """
        try:
            # Format messages for Ollama
            prompt = ""
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    prompt += f"System: {content}\n"
                elif role == "user":
                    prompt += f"User: {content}\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n"
            
            # Prepare request data
            data = {
                "model": model,
                "prompt": prompt.strip(),
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                }
            }
            
            if seed is not None:
                data["options"]["seed"] = seed
            if max_tokens is not None:
                data["options"]["num_predict"] = max_tokens
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=None)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Chat completion failed: {response.status}")
                    
                    # Process streaming response
                    response_text = ""
                    async for line in response.content:
                        if not line:
                            continue
                            
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                text = chunk["response"]
                                response_text += text
                                print(text, end="", flush=True)
                                
                            if chunk.get("done", False):
                                break
                                
                        except json.JSONDecodeError as e:
                            self.logger.warning(f"Failed to decode response chunk: {e}")
                            continue
                    
                    # Return formatted response
                    return {
                        "choices": [{
                            "message": {
                                "role": "assistant",
                                "content": response_text
                            }
                        }]
                    }
                    
        except Exception as e:
            self.logger.error(f"Error in chat completion: {str(e)}")
            raise