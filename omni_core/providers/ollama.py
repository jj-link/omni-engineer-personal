"""Ollama provider implementation for model interaction."""
import aiohttp
from typing import Dict, List, Optional, Any
from ..config import ProviderConfig


class OllamaProvider:
    """Provider implementation for Ollama API."""
    
    def __init__(self, config: ProviderConfig):
        """Initialize Ollama provider with configuration.
        
        Args:
            config: Provider configuration containing base URL and model settings
        """
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from Ollama.
        
        Returns:
            List of model information dictionaries
        """
        session = aiohttp.ClientSession()
        try:
            async with session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status != 200:
                        raise Exception(f"Failed to list models: {response.status}")
                    data = await response.json()
                    return data.get("models", [])
        finally:
            await session.close()

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate chat completion using Ollama.
        
        Args:
            messages: List of message dictionaries with role and content
            temperature: Optional sampling temperature
            top_p: Optional nucleus sampling parameter
            max_tokens: Optional maximum tokens to generate
            
        Returns:
            Response dictionary containing generated text
        """
        # Convert messages to Ollama format
        system_msg = next((msg["content"] for msg in messages if msg["role"] == "system"), None)
        prompt = ""
        
        if system_msg:
            prompt = f"<s>[INST] <<SYS>>\n{system_msg}\n<</SYS>>\n\n"
        
        for msg in messages:
            if msg["role"] == "system":
                continue
            elif msg["role"] == "user":
                prompt += f"[INST] {msg['content']} [/INST]"
            else:
                prompt += f" {msg['content']} </s>"
                
        data = {
            "model": self.config.model,
            "prompt": prompt.strip(),
            "stream": False,
        }
        
        if temperature is not None:
            data["temperature"] = temperature
        if top_p is not None:
            data["top_p"] = top_p
        if max_tokens is not None:
            data["num_predict"] = max_tokens
            
        session = aiohttp.ClientSession()
        try:
            async with session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=data
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Chat completion failed: {response.status}")
                    result = await response.json()
                    
                    return {
                        "choices": [{

                                "role": "assistant",
                                "content": result.get("response", "")
                            }
                        }]
                    }
        finally:
            await session.close()
