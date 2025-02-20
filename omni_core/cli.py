"""Command-line interface configuration for Omni Engineer."""

import argparse
from typing import Optional
from dataclasses import dataclass

@dataclass
class CliConfig:
    """Configuration from command-line arguments."""
    provider: str
    model: str
    temperature: float = 0.7
    top_p: float = 0.95
    seed: Optional[int] = None
    max_tokens: Optional[int] = None
    list_models: bool = False

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
    if value.lower() not in ["ollama"]:
        raise argparse.ArgumentTypeError(
            "Provider must be: ollama"
        )
    return value.lower()

def get_cli_config() -> CliConfig:
    """Get configuration from command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Omni Engineer - Multi-Model AI Engineering Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use Ollama with llama2
  omni-engineer --provider ollama --model llama2

  # List available models
  omni-engineer --provider ollama --list-models

  # Use custom parameters
  omni-engineer --provider ollama --model llama2 --temperature 0.8 --top-p 0.9
"""
    )

    # Provider and model
    parser.add_argument(
        "--provider",
        type=validate_provider,
        default="ollama",
        help="Model provider (ollama)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="llama2",
        help="Model name"
    )

    # Model parameters
    parser.add_argument(
        "--temperature",
        type=validate_temperature,
        default=0.7,
        help="Sampling temperature (0.0-1.0)"
    )
    parser.add_argument(
        "--top-p",
        type=validate_top_p,
        default=0.95,
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
        help="Maximum tokens to generate"
    )

    # Utility flags
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models"
    )

    args = parser.parse_args()
    return CliConfig(
        provider=args.provider,
        model=args.model,
        temperature=args.temperature,
        top_p=args.top_p,
        seed=args.seed,
        max_tokens=args.max_tokens,
        list_models=args.list_models
    )
