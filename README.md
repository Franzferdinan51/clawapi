# ClawAPI Linux

Model Switcher & Key Vault for OpenClaw - Linux Version

A cross-platform CLI tool for managing AI API keys and switching models in OpenClaw.

## Features

- 🔐 **Secure Key Storage** - Encrypted API key storage using Fernet encryption
- 🔄 **Model Switching** - Quick model selection from 15+ providers
- 📋 **Provider Support** - OpenAI, Anthropic, Google, xAI, Groq, Mistral, Ollama, MiniMax, Zhipu AI
- 🐧 **Linux Native** - Built for Linux using Python

## Installation

```bash
cd clawapi-linux
./install.sh
```

Or manually:
```bash
pip install cryptography
chmod +x clawapi-linux.py
sudo cp clawapi-linux.py /usr/local/bin/clawapi-linux
```

## Usage

### List Providers
```bash
clawapi-linux list
```

### Add API Key
```bash
clawapi-linux add openai sk-xxx...
clawapi-linux add anthropic sk-ant-xxx...
clawapi-linux add google AIza.xxx...
```

### List Models
```bash
clawapi-linux models openai
clawapi-linux models anthropic
```

### Set Default Model
```bash
clawapi-linux set openai gpt-4o
clawapi-linux set anthropic claude-sonnet-4-6
```

### Show Key (Masked)
```bash
clawapi-linux show openai
```

### Remove Key
```bash
clawapi-linux remove openai
```

## Supported Providers

| Provider | Status | Local |
|----------|--------|-------|
| OpenAI | ✓ | No |
| Anthropic | ✓ | No |
| Google | ✓ | No |
| xAI | ✓ | No |
| Groq | ✓ | No |
| Mistral | ✓ | No |
| Ollama | ✓ | Yes |
| MiniMax | ✓ | No |
| Zhipu AI (GLM) | ✓ | No |

## Security

- API keys are encrypted using Fernet (symmetric encryption)
- Master key stored in `~/.config/clawapi/.master.key` (mode 600)
- Keys stored in `~/.config/clawapi/keys.enc` (mode 600)

## Requirements

- Python 3.8+
- cryptography library

## License

MIT
