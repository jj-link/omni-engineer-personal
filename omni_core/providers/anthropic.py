"""
Anthropic provider for chat completion and model management.
"""

import os
import aiohttp
import json
from typing import List, Dict, Any, Optional

class AnthropicProvider:
    """Provider for Anthropic's Claude models."""
    
    def __init__(self, base_url: str = "https://api.anthropic.com/v1"):
        """Initialize the Anthropic provider.
        
        Args:
            base_url: Base URL for the Anthropic API
        """
        self.base_url = base_url
        self.model = "anthropic/claude-haiku"  # Default model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    async def list_models(self) -> List[Dict[str, Any]]:
        """List available Anthropic models.
        
        Returns:
            List of available models with their metadata
        """
        # Anthropic doesn't have a list models endpoint, so we return the static list
        return [
            {
                "name": "anthropic/claude-haiku",
                "description": "Fast and affordable model, including vision capabilities",
                "capabilities": ["chat", "vision", "fast"]
            },
            {
                "name": "anthropic/claude-sonnet",
                "description": "Latest version of cost-optimized model with excellent reasoning and coding",
                "capabilities": ["chat", "code"]
            },
            {
                "name": "anthropic/claude-opus",
                "description": "Advanced model for nuanced reasoning, math, coding and more",
                "capabilities": ["chat", "code", "math"]
            }
        ]

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a chat completion using Anthropic's API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use for completion
            temperature: Sampling temperature (0-1)
            top_p: Nucleus sampling parameter (0-1)
            seed: Random seed for reproducibility
            **kwargs: Additional parameters to pass to the API
        
        Returns:
            API response containing the completion
            
        Raises:
            Exception: If the API request fails
        """
        if not model:
            model = self.model
            
        # Remove 'anthropic/' prefix if present
        if '/' in model:
            model = model.split('/')[-1]
            
        # Convert messages to Anthropic format
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
                
        # Prepare request data
        data = {
            "model": model,
            "messages": user_messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": kwargs.get("max_tokens", 2048)
        }
        
        if system_message:
            data["system"] = system_message
            
        if seed is not None:
            data["seed"] = seed
            
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error: {error_text}")
                    
                result = await response.json()
                
                # Convert Anthropic response format to our standard format
                return {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": result["content"][0]["text"]
                        }
                    }],
                    "usage": result.get("usage", {}),
                    "model": model
                }

    async def close(self):
        """Clean up resources."""
        pass  # No cleanup needed for this provider
