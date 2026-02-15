# ClawAPI
#model-switcher #key-vault #openclaw

**Model Switcher & Key Vault for OpenClaw - Cross-platform**

A cross-platform CLI + Web UI for managing AI API keys and switching models in [OpenClaw](https://openclaw.app).

> **Original macOS App by [Gogo6969](https://github.com/Gogo6969/clawapi)**  
> This is a Linux/Windows port with a Flask-based web UI, inspired by the original macOS application.

Supports OpenAI, Anthropic, Google, xAI, Groq, Mistral, Ollama, MiniMax, Zhipu AI, OpenRouter, Cerebras, HuggingFace, Kimi Coding, OpenCode, and Vercel AI Gateway.

---

## Install

### Linux/macOS
```bash
curl -fsSL https://raw.githubusercontent.com/Franzferdinan51/clawapi/main/install.sh | bash
```

Or manually:
```bash
cd clawapi-linux
pip install flask cryptography requests
chmod +x clawapi.py
sudo cp clawapi.py /usr/local/bin/clawapi
```

### Windows
```bash
# Run the installer
install.bat

# Or manual setup
python -m venv .venv
.venv\Scripts\activate.bat
pip install flask cryptography requests
python clawapi.py
```

---

## Features

- 🔐 **Secure Key Storage** - Encrypted API key storage (Fernet/AES)
- 🔄 **Model Switching** - Quick model selection from 15+ providers
- 📋 **15+ Providers** - OpenAI, Anthropic, Google, xAI, Groq, Mistral, Ollama, MiniMax, Zhipu AI, OpenRouter, Cerebras, HuggingFace, Kimi Coding, OpenCode, Vercel
- 🖥️ **Web UI** - Flask-based dashboard (port 5001)
- 🔁 **Auto-Sync** - Changes written directly to OpenClaw config
- 🌐 **Cross-Platform** - Linux, macOS, Windows

---

## Usage

### CLI
```bash
clawapi list                      # List all providers
clawapi add openai sk-xxx...     # Add API key
clawapi models openai            # List models for provider
clawapi set openai gpt-4o       # Set default model
clawapi show openai             # Show masked key
clawapi remove openai           # Remove provider
```

### Web UI
```bash
# Linux/macOS
source .venv/bin/activate
python webui.py

# Windows
.venv\Scripts\activate.bat
python webui.py
```

Then open http://localhost:5001 (or http://100.106.80.61:5001 via Tailscale)

---

## Configuration

- **Linux**: `~/.config/clawapi/`
- **macOS**: `~/Library/Application Support/ClawAPI/`
- **Windows**: `%APPDATA%\ClawAPI\`

---

## Credit

> **Original ClawAPI macOS App** - Created by [Gogo6969](https://github.com/Gogo6969/clawapi)  
> A native macOS app that lets you switch AI models and securely manage API keys for OpenClaw.
> 
> Features include: One-click model switching, Secure key vault (macOS Keychain), 15+ providers, Auto-sync to OpenClaw, Usage dashboard, VPS support via SSH.
>
> This Linux/Windows version is inspired by and compatible with the original.

---

## Security

- API keys encrypted with Fernet (AES-128)
- Master key stored in config directory (mode 600)
- Keys stored encrypted on disk

---

## License

MIT - Based on [ClawAPI by Gogo6969](https://github.com/Gogo6969/clawapi)

---

## Links

- **Original macOS App**: https://github.com/Gogo6969/clawapi
- **This Repository**: https://github.com/Franzferdinan51/clawapi
- **OpenClaw**: https://openclaw.app
