"""Chat module for Omni Engineer."""

import json
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import asyncio
import time

from .config import Configuration
from .providers.cborg import chat_completion as cborg_chat
from anthropic import Anthropic, APIStatusError, APIError

console = Console()

@dataclass
class TokenUsage:
    """Token usage statistics."""
    input: int = 0
    output: int = 0
    cache_write: int = 0
    cache_read: int = 0

class ChatManager:
    """Manages chat interactions with different providers."""
    
    def __init__(self):
        """Initialize chat manager."""
        self.config = Configuration()
        self.conversation_history: List[Dict[str, Any]] = []
        self.token_usage = TokenUsage()
        
        # Initialize provider-specific clients
        if self.config.provider_config.name == "anthropic":
            self.anthropic_client = Anthropic(api_key=self.config.provider_config.api_key)
    
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ) -> Tuple[str, List[Dict[str, Any]], bool]:
        """Send a chat request to the current provider.
        
        Args:
            messages: List of message dictionaries
            tools: Optional list of available tools
            system_prompt: Optional system prompt
            max_retries: Maximum number of retries on failure
            retry_delay: Initial delay between retries in seconds
            
        Returns:
            Tuple of (response text, tool uses, exit flag)
        """
        provider = self.config.provider_config.name
        
        for attempt in range(max_retries):
            try:
                if provider == "anthropic":
                    return await self._chat_anthropic(messages, tools, system_prompt)
                elif provider == "cborg":
                    return await self._chat_cborg(messages, tools, system_prompt)
                elif provider == "ollama":
                    return await self._chat_ollama(messages, tools, system_prompt)
                else:
                    raise ValueError(f"Unsupported provider: {provider}")
                
            except (APIStatusError, APIError) as e:
                if isinstance(e, APIStatusError) and e.status_code == 429 and attempt < max_retries - 1:
                    console.print(Panel(
                        f"Rate limit exceeded. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})",
                        title="API Error",
                        style="bold yellow"
                    ))
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    console.print(Panel(f"API Error: {str(e)}", title="API Error", style="bold red"))
                    return "I'm sorry, there was an error communicating with the AI. Please try again.", [], False
        
        console.print(Panel(
            "Max retries reached. Unable to communicate with the AI.",
            title="Error",
            style="bold red"
        ))
        return "I'm sorry, there was a persistent error communicating with the AI. Please try again later.", [], False
    
    async def _chat_anthropic(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        system_prompt: Optional[str]
    ) -> Tuple[str, List[Dict[str, Any]], bool]:
        """Handle chat with Anthropic's Claude."""
        response = await self.anthropic_client.beta.prompt_caching.messages.create(
            model=self.config.provider_config.model,
            max_tokens=8000,
            system=[
                {
                    "type": "text",
                    "text": system_prompt or "",
                    "cache_control": {"type": "ephemeral"}
                },
                {
                    "type": "text",
                    "text": json.dumps(tools) if tools else "",
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=messages,
            tools=tools,
            tool_choice={"type": "auto"},
            extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
        )
        
        # Update token usage
        self.token_usage.input += response.usage.input_tokens
        self.token_usage.output += response.usage.output_tokens
        self.token_usage.cache_write = response.usage.cache_creation_input_tokens
        self.token_usage.cache_read = response.usage.cache_read_input_tokens
        
        # Process response
        assistant_response = ""
        exit_continuation = False
        tool_uses = []
        
        for content_block in response.content:
            if content_block.type == "text":
                assistant_response += content_block.text
                if "CONTINUE" not in content_block.text:
                    exit_continuation = True
            elif content_block.type == "tool_use":
                tool_uses.append(content_block)
        
        return assistant_response, tool_uses, exit_continuation
    
    async def _chat_cborg(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        system_prompt: Optional[str]
    ) -> Tuple[str, List[Dict[str, Any]], bool]:
        """Handle chat with CBORG."""
        # Add system prompt if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Call CBORG chat completion
        response = await cborg_chat(
            messages,
            temperature=self.config.provider_config.parameters.temperature,
            top_p=self.config.provider_config.parameters.top_p,
            max_tokens=self.config.provider_config.parameters.max_tokens,
            seed=self.config.provider_config.parameters.seed
        )
        
        # Extract response content
        assistant_message = response["choices"][0]["message"]
        assistant_response = assistant_message["content"]
        
        # Check for continuation
        exit_continuation = "CONTINUE" not in assistant_response
        
        # CBORG doesn't support tools yet, so return empty list
        tool_uses = []
        
        return assistant_response, tool_uses, exit_continuation
    
    async def _chat_ollama(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        system_prompt: Optional[str]
    ) -> Tuple[str, List[Dict[str, Any]], bool]:
        """Handle chat with Ollama."""
        # TODO: Implement Ollama chat
        raise NotImplementedError("Ollama chat not yet implemented")
