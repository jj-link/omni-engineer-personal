"""Command-line interface configuration for Omni Engineer."""

import argparse
from typing import Dict, Any, Optional
from dataclasses import dataclass
from .config import PROVIDERS

@dataclass
class CliConfig:
    """Configuration from command-line arguments."""
    provider: str
    model: str
    temperature: float = 0.7
    top_p: float = 0.9
    seed: Optional[int] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    auto_mode: Optional[int] = None

def validate_temperature(value: str) -> float:
    """Validate temperature is between 0 and 1."""
    try:
        temp = float(value)
        if not 0 <= temp <= 1:
            raise ValueError
        return temp
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Temperature must be a float between 0 and 1"
        )

def validate_top_p(value: str) -> float:
    """Validate top_p is between 0 and 1."""
    try:
        top_p = float(value)
        if not 0 <= top_p <= 1:
            raise ValueError
        return top_p
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Top-p must be a float between 0 and 1"
        )

def validate_provider(value: str) -> str:
    """Validate provider is supported."""
    if value not in PROVIDERS:
        raise argparse.ArgumentTypeError(
            f"Provider must be one of: {', '.join(PROVIDERS.keys())}"
        )
    return value

def parse_args() -> CliConfig:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Omni Engineer - Multi-Model AI Engineering Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use Ollama with CodeLlama
  omni-engineer --provider ollama --model codellama

  # Use CBORG with custom parameters
  omni-engineer --provider cborg --model lbl/cborg-coder:latest --temperature 0.8

  # Start in auto mode with 5 iterations
  omni-engineer --provider ollama --model codellama --auto-mode 5
"""
    )

    # Required arguments
    parser.add_argument(
        "--provider",
        type=validate_provider,
        required=True,
        help="Model provider (ollama/cborg)"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model name/path"
    )

    # Optional arguments
    parser.add_argument(
        "--temperature",
        type=validate_temperature,
        default=0.7,
        help="Sampling temperature (0.0-1.0)"
    )
    parser.add_argument(
        "--top-p",
        type=validate_top_p,
        default=0.9,
        help="Nucleus sampling parameter (0.0-1.0)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        help="Maximum tokens in response"
    )
    parser.add_argument(
        "--system-prompt",
        type=str,
        help="Custom system prompt"
    )
    parser.add_argument(
        "--auto-mode",
        type=int,
        help="Start in auto mode with specified iterations"
    )

    args = parser.parse_args()
    return CliConfig(
        provider=args.provider,
        model=args.model,
        temperature=args.temperature,
        top_p=args.top_p,
        seed=args.seed,
        max_tokens=args.max_tokens,
        system_prompt=args.system_prompt,
        auto_mode=args.auto_mode
    )

def get_cli_config() -> Dict[str, Any]:
    """Get configuration from command-line arguments."""
    config = parse_args()
    return {
        "provider": config.provider,
        "model": config.model,
        "parameters": {
            "temperature": config.temperature,
            "top_p": config.top_p,
            "seed": config.seed,
            "max_tokens": config.max_tokens
        },
        "system_prompt": config.system_prompt,
        "auto_mode": config.auto_mode
    }
