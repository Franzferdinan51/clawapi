#!/usr/bin/env python3
"""
ClawAPI - Model Switcher & Key Vault for OpenClaw
Cross-platform: Linux, macOS, Windows
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import platform

# Detect OS
def get_os():
    return platform.system().lower()

# Cross-platform config directory
def get_config_dir():
    os_name = get_os()
    if os_name == "windows":
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        return base / "ClawAPI"
    elif os_name == "darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "ClawAPI"
    else:  # Linux
        return Path.home() / ".config" / "clawapi"

# Supported providers (same as macOS v1.4)
PROVIDERS = {
    "openai": {"name": "OpenAI", "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "o1", "o1-mini", "o3-mini", "gpt-4.5"], "default_model": "gpt-4o"},
    "anthropic": {"name": "Anthropic", "models": ["claude-opus-4-5", "claude-sonnet-4-6", "claude-haiku-3-5", "claude-3-5-sonnet", "claude-3-opus", "claude-3-sonnet"], "default_model": "claude-sonnet-4-6"},
    "google": {"name": "Google", "models": ["gemini-2.0-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-2.5-pro"], "default_model": "gemini-2.0-flash"},
    "xai": {"name": "xAI", "models": ["grok-2", "grok-2-vision", "grok-beta", "grok-vision-beta", "grok-3", "grok-3-mini"], "default_model": "grok-2"},
    "groq": {"name": "Groq", "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "llama-3.1-70b-versatile", "gemma2-9b-it", "qwen-2.5-32b"], "default_model": "llama-3.3-70b-versatile"},
    "mistral": {"name": "Mistral", "models": ["mistral-large-latest", "mistral-small-latest", "codestral-latest", "pixtral-large-mistral-nemo"], "default_model": "mistral-small-latest"},
    "ollama": {"name": "Ollama", "models": ["llama3.3", "llama3.2", "llama3.1", "qwen2.5", "mistral", "codellama", "phi4", "deepseek-llm", "command-r"], "default_model": "llama3.3", "local": True},
    "minimax": {"name": "MiniMax", "models": ["MiniMax-M2.1", "MiniMax-M2.1-lightning", "abab6.5s-chat", "abab6.5g-chat", "abab6"], "default_model": "MiniMax-M2.1"},
    "zai": {"name": "Zhipu AI (GLM)", "models": ["glm-4", "glm-4-flash", "glm-4-plus", "glm-4v", "glm-5", "glm-4-vision"], "default_model": "glm-4"},
    "openrouter": {"name": "OpenRouter", "models": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "google/gemini-pro-1.5", "meta-llama/llama-3.1-70b-instruct"], "default_model": "anthropic/claude-3.5-sonnet"},
    "cerebras": {"name": "Cerebras", "models": ["llama-3.3-70b", "llama-3.1-70b", "mixtral-8x7b", "qwen-2.5-32b"], "default_model": "llama-3.3-70b"},
    "huggingface": {"name": "HuggingFace", "models": ["meta-llama/Llama-3.3-70B-Instruct", "Qwen/Qwen2.5-72B-Instruct"], "default_model": "meta-llama/Llama-3.3-70B-Instruct"},
    "kimi-coding": {"name": "Kimi Coding", "models": ["kimi-coder-flash", "kimi-coder", "kimi-long"], "default_model": "kimi-coder-flash"},
    "opencode": {"name": "OpenCode", "models": ["opencode", "opencode-32b", "opencode-8b"], "default_model": "opencode"},
    "vercel-ai-gateway": {"name": "Vercel AI Gateway", "models": ["gpt-4o", "claude-3.5-sonnet", "gemini-1.5-pro"], "default_model": "gpt-4o"},
}

CONFIG_DIR = get_config_dir()
KEYS_FILE = CONFIG_DIR / "keys.enc"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Ensure config directory exists
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def get_master_key():
    key_file = CONFIG_DIR / ".master.key"
    if key_file.exists():
        return key_file.read_bytes()
    key = Fernet.generate_key()
    key_file.write_bytes(key)
    os.chmod(str(key_file), 0o600)
    return key

def encrypt_key(key):
    f = Fernet(get_master_key())
    return base64.b64encode(f.encrypt(key.encode())).decode()

def decrypt_key(encrypted):
    f = Fernet(get_master_key())
    return f.decrypt(base64.b64decode(encrypted.encode())).decode()

def load_keys():
    if not KEYS_FILE.exists():
        return {}
    try:
        with open(KEYS_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)
    os.chmod(str(KEYS_FILE), 0o600)

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {"selected_models": {}}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def list_providers():
    keys = load_keys()
    config = load_config()
    print(f"📋 Providers ({get_os().title()}):")
    print("-" * 40)
    for pid, pdata in PROVIDERS.items():
        status = "✓" if pid in keys else "✗"
        model = config.get("selected_models", {}).get(pid, pdata.get("default_model", ""))
        print(f"  {status} {pdata['name']:<15} {model}")

def add_provider(pid, api_key):
    if pid not in PROVIDERS:
        print(f"Error: Unknown provider '{pid}'")
        return
    keys = load_keys()
    keys[pid] = encrypt_key(api_key)
    save_keys(keys)
    print(f"✓ Added {PROVIDERS[pid]['name']}")

def list_models(pid):
    if pid not in PROVIDERS:
        print(f"Error: Unknown provider '{pid}'")
        return
    print(f"📦 Models for {PROVIDERS[pid]['name']}:")
    for m in PROVIDERS[pid]['models']:
        print(f"  - {m}")

def set_model(pid, model):
    config = load_config()
    if "selected_models" not in config:
        config["selected_models"] = {}
    config["selected_models"][pid] = model
    save_config(config)
    
    # Also update OpenClaw config
    openclaw_path = Path.home() / ".openclaw" / "openclaw.json"
    if openclaw_path.exists():
        try:
            with open(openclaw_path) as f:
                oc = json.load(f)
            oc['defaultModel'] = model
            oc['model'] = model
            with open(openclaw_path, 'w') as f:
                json.dump(oc, f, indent=2)
            print(f"✓ Set {model} as default (also synced to OpenClaw)")
        except Exception as e:
            print(f"✓ Set {model} as default (OpenClaw sync failed: {e})")
    else:
        print(f"✓ Set {model} as default")

def show_key(pid):
    keys = load_keys()
    if pid not in keys:
        print(f"{PROVIDERS[pid]['name']}: No key stored")
        return
    print(f"{PROVIDERS[pid]['name']}: {decrypt_key(keys[pid][:10])}...{decrypt_key(keys[pid])[-4:]}")

def remove_provider(pid):
    keys = load_keys()
    if pid in keys:
        del keys[pid]
        save_keys(keys)
        config = load_config()
        if "selected_models" in config and pid in config["selected_models"]:
            del config["selected_models"][pid]
            save_config(config)
        print(f"✓ Removed {PROVIDERS[pid]['name']}")
    else:
        print(f"Provider not configured")

def main():
    parser = argparse.ArgumentParser(description="ClawAPI - Model Switcher for OpenClaw")
    parser.add_argument("command", choices=["list", "add", "models", "set", "show", "remove"], help="Command to run")
    parser.add_argument("args", nargs="*", help="Arguments for command")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_providers()
    elif args.command == "add":
        if len(args.args) < 2:
            print("Usage: clawapi add <provider> <api_key>")
            return
        add_provider(args.args[0], args.args[1])
    elif args.command == "models":
        if len(args.args) < 1:
            print("Usage: clawapi models <provider>")
            return
        list_models(args.args[0])
    elif args.command == "set":
        if len(args.args) < 2:
            print("Usage: clawapi set <provider> <model>")
            return
        set_model(args.args[0], args.args[1])
    elif args.command == "show":
        if len(args.args) < 1:
            print("Usage: clawapi show <provider>")
            return
        show_key(args.args[0])
    elif args.command == "remove":
        if len(args.args) < 1:
            print("Usage: clawapi remove <provider>")
            return
        remove_provider(args.args[0])

if __name__ == "__main__":
    main()
