#!/usr/bin/env python3
"""
ClawAPI Linux - Model Switcher & Key Vault for OpenClaw
Cross-platform API key management and model switching for Linux
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Dict, List, Optional, Optional
import base64
import hashlib

CONFIG_DIR = Path.home() / ".config" / "clawapi"
KEYS_FILE = CONFIG_DIR / "keys.enc"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Supported providers
PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "o1", "o1-mini", "o3-mini"],
        "default_model": "gpt-4o"
    },
    "anthropic": {
        "name": "Anthropic",
        "models": ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-3-5", "claude-3-5-sonnet", "claude-3-opus", "claude-3-sonnet"],
        "default_model": "claude-sonnet-4-6"
    },
    "google": {
        "name": "Google",
        "models": ["gemini-2.0-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-flash-8b"],
        "default_model": "gemini-2.0-flash"
    },
    "xai": {
        "name": "xAI",
        "models": ["grok-2", "grok-2-vision", "grok-beta"],
        "default_model": "grok-2"
    },
    "groq": {
        "name": "Groq",
        "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "llama-3.1-70b-versatile", "gemma2-9b-it"],
        "default_model": "llama-3.3-70b-versatile"
    },
    "mistral": {
        "name": "Mistral",
        "models": ["mistral-large-latest", "mistral-small-latest", "codestral-latest"],
        "default_model": "mistral-small-latest"
    },
    "ollama": {
        "name": "Ollama",
        "models": ["llama3.3", "llama3.2", "llama3.1", "qwen2.5", "mistral", "codellama", "phi4"],
        "default_model": "llama3.3",
        "local": True
    },
    "minimax": {
        "name": "MiniMax",
        "models": ["MiniMax-M2.1", "MiniMax-M2.1-lightning"],
        "default_model": "MiniMax-M2.1"
    },
    "zai": {
        "name": "Zhipu AI (GLM)",
        "models": ["glm-4", "glm-4-flash", "glm-4-plus", "glm-4v", "glm-5"],
        "default_model": "glm-4"
    }
}

def get_master_key() -> bytes:
    """Get or create master encryption key"""
    key_file = CONFIG_DIR / ".master.key"
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    if key_file.exists():
        return key_file.read_bytes()
    
    # Generate new key
    key = Fernet.generate_key()
    key_file.write_bytes(key)
    os.chmod(str(key_file), 0o600)
    return key

def encrypt_key(key: str) -> str:
    """Encrypt an API key"""
    f = Fernet(get_master_key())
    return base64.b64encode(f.encrypt(key.encode())).decode()

def decrypt_key(encrypted: str) -> str:
    """Decrypt an API key"""
    f = Fernet(get_master_key())
    return f.decrypt(base64.b64decode(encrypted.encode())).decode()

def load_keys() -> Dict[str, str]:
    """Load encrypted keys"""
    if not KEYS_FILE.exists():
        return {}
    
    try:
        data = json.loads(KEYS_FILE.read_text())
        return {provider: decrypt_key(encrypted) for provider, encrypted in data.items()}
    except:
        return {}

def save_keys(keys: Dict[str, str]):
    """Save encrypted keys"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    encrypted = {provider: encrypt_key(key) for provider, key in keys.items()}
    KEYS_FILE.write_text(json.dumps(encrypted))
    os.chmod(str(KEYS_FILE), 0o600)

def add_key(provider: str, api_key: str):
    """Add or update an API key"""
    provider = provider.lower()
    if provider not in PROVIDERS:
        print(f"Error: Unknown provider '{provider}'")
        print(f"Supported: {', '.join(PROVIDERS.keys())}")
        sys.exit(1)
    
    keys = load_keys()
    keys[provider] = api_key
    save_keys(keys)
    print(f"✓ Added {PROVIDERS[provider]['name']} API key")

def list_providers():
    """List all providers and their status"""
    keys = load_keys()
    print("\n📋 Providers:")
    print("-" * 40)
    
    for provider, info in PROVIDERS.items():
        status = "✓ Configured" if provider in keys else "✗ Not configured"
        local = " (Local)" if info.get("local") else ""
        print(f"  {info['name']:15} {status:20} {local}")
    print()

def list_models(provider: str):
    """List models for a provider"""
    provider = provider.lower()
    if provider not in PROVIDERS:
        print(f"Error: Unknown provider '{provider}'")
        sys.exit(1)
    
    info = PROVIDERS[provider]
    print(f"\n📦 Models for {info['name']}:")
    print("-" * 40)
    for model in info["models"]:
        print(f"  - {model}")
    print()

def get_openclaw_config_path() -> Optional[Path]:
    """Get OpenClaw config path"""
    config_paths = [
        Path.home() / ".openclaw" / "openclaw.json",
    ]
    
    for path in config_paths:
        if path.exists():
            return path
    
    return None

def sync_to_openclaw(provider: str, model: str, api_key: str):
    """Sync provider to OpenClaw config"""
    config_path = get_openclaw_config_path()
    if not config_path:
        print("⚠ OpenClaw config not found")
        return False
    
    try:
        config = json.loads(config_path.read_text())
    except:
        config = {}
    
    # Ensure models section exists
    if "models" not in config:
        config["models"] = {}
    if "providers" not in config["models"]:
        config["models"]["providers"] = {}
    
    # Add provider
    provider_key = f"{provider}:default"
    config["models"]["providers"][provider_key] = {
        "provider": provider,
        "model": model,
        "apiKey": api_key
    }
    
    # Write config
    config_path.write_text(json.dumps(config, indent=2))
    print(f"✓ Synced to OpenClaw config")
    
    # Suggest restart
    print(f"ℹ Run 'openclaw gateway restart' to apply changes")
    return True

def set_model(provider: str, model: Optional[str] = None):
    """Set the default model for a provider in OpenClaw"""
    provider = provider.lower()
    if provider not in PROVIDERS:
        print(f"Error: Unknown provider '{provider}'")
        sys.exit(1)
    
    # Check if key exists
    keys = load_keys()
    if provider not in keys:
        print(f"Error: No API key found for {PROVIDERS[provider]['name']}")
        print(f"Run: clawapi-linux add {provider} YOUR_API_KEY")
        sys.exit(1)
    
    if model is None:
        model = PROVIDERS[provider]["default_model"]
    
    print(f"Setting {provider} model to {model}...")
    
    # Auto-sync to OpenClaw
    sync_to_openclaw(provider, model, keys[provider])

def remove_key(provider: str):
    """Remove an API key"""
    provider = provider.lower()
    keys = load_keys()
    
    if provider in keys:
        del keys[provider]
        save_keys(keys)
        print(f"✓ Removed {PROVIDERS[provider]['name']} API key")
    else:
        print(f"No key found for {provider}")

def show_key(provider: str):
    """Show (partially masked) API key"""
    provider = provider.lower()
    keys = load_keys()
    
    if provider not in keys:
        print(f"No key found for {provider}")
        return
    
    key = keys[provider]
    masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
    print(f"{provider}: {masked}")

def main():
    parser = argparse.ArgumentParser(
        description="ClawAPI Linux - Model Switcher & Key Vault for OpenClaw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clawapi-linux list                    # List all providers
  clawapi-linux add openai sk-xxx       # Add OpenAI API key
  clawapi-linux models anthropic         # List Anthropic models
  clawapi-linux set openai gpt-4o      # Set default model
  clawapi-linux show openai             # Show (masked) key
  clawapi-linux remove openai           # Remove key
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List providers
    subparsers.add_parser("list", help="List all providers")
    
    # Add key
    add_parser = subparsers.add_parser("add", help="Add API key")
    add_parser.add_argument("provider", help="Provider name")
    add_parser.add_argument("api_key", help="API key")
    
    # List models
    models_parser = subparsers.add_parser("models", help="List models for provider")
    models_parser.add_argument("provider", help="Provider name")
    
    # Set model
    set_parser = subparsers.add_parser("set", help="Set default model")
    set_parser.add_argument("provider", help="Provider name")
    set_parser.add_argument("model", nargs="?", help="Model name (optional)")
    
    # Show key
    show_parser = subparsers.add_parser("show", help="Show masked API key")
    show_parser.add_argument("provider", help="Provider name")
    
    # Remove key
    remove_parser = subparsers.add_parser("remove", help="Remove API key")
    remove_parser.add_argument("provider", help="Provider name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        list_providers()
        return
    
    if args.command == "list":
        list_providers()
    elif args.command == "add":
        add_key(args.provider, args.api_key)
    elif args.command == "models":
        list_models(args.provider)
    elif args.command == "set":
        set_model(args.provider, args.model)
    elif args.command == "show":
        show_key(args.provider)
    elif args.command == "remove":
        remove_key(args.provider)

if __name__ == "__main__":
    main()
