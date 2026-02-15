#!/usr/bin/env python3
"""
ClawAPI Linux - Full Web UI
Model Switcher & Key Vault for OpenClaw - Linux Version
Complete implementation matching macOS ClawAPI
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from cryptography.fernet import Fernet
import base64
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clawapi-linux-secret-key-change-in-production'

# Config paths
CONFIG_DIR = Path.home() / ".config" / "clawapi"
KEYS_FILE = CONFIG_DIR / "keys.enc"
CONFIG_FILE = CONFIG_DIR / "config.json"
MASTER_KEY_FILE = CONFIG_DIR / ".master.key"
OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"

# Ensure config directory exists
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Supported providers (matching CLI + new providers from v1.4)
PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "o1", "o1-mini", "o3-mini", "gpt-4.5"],
        "default_model": "gpt-4o",
        "billing_url": "https://platform.openai.com/settings/organization/usage",
        "local": False
    },
    "anthropic": {
        "name": "Anthropic",
        "models": ["claude-opus-4-5", "claude-sonnet-4-6", "claude-haiku-3-5", "claude-3-5-sonnet", "claude-3-opus", "claude-3-sonnet"],
        "default_model": "claude-sonnet-4-6",
        "billing_url": "https://console.anthropic.com/settings/billing",
        "local": False
    },
    "google": {
        "name": "Google",
        "models": ["gemini-2.0-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-2.5-pro"],
        "default_model": "gemini-2.0-flash",
        "billing_url": "https://aistudio.google.com/app/billing",
        "local": False
    },
    "xai": {
        "name": "xAI",
        "models": ["grok-2", "grok-2-vision", "grok-beta", "grok-vision-beta", "grok-3", "grok-3-mini"],
        "default_model": "grok-2",
        "billing_url": "https://console.x.ai",
        "local": False
    },
    "groq": {
        "name": "Groq",
        "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "llama-3.1-70b-versatile", "gemma2-9b-it", "qwen-2.5-32b"],
        "default_model": "llama-3.3-70b-versatile",
        "billing_url": "https://console.groq.com/usage",
        "local": False
    },
    "mistral": {
        "name": "Mistral",
        "models": ["mistral-large-latest", "mistral-small-latest", "codestral-latest", "pixtral-large-mistral-nemo"],
        "default_model": "mistral-small-latest",
        "billing_url": "https://console.mistral.ai/home",
        "local": False
    },
    "ollama": {
        "name": "Ollama",
        "models": ["llama3.3", "llama3.2", "llama3.1", "qwen2.5", "mistral", "codellama", "phi4", "deepseek-llm", "command-r"],
        "default_model": "llama3.3",
        "local": True,
        "billing_url": None
    },
    "minimax": {
        "name": "MiniMax",
        "models": ["MiniMax-M2.1", "MiniMax-M2.1-lightning", "abab6.5s-chat", "abab6.5g-chat", "abab6"],
        "default_model": "MiniMax-M2.1",
        "billing_url": "https://platform.minimax.io/",
        "local": False
    },
    "zai": {
        "name": "Zhipu AI (GLM)",
        "models": ["glm-4", "glm-4-flash", "glm-4-plus", "glm-4v", "glm-5", "glm-4-vision"],
        "default_model": "glm-4",
        "billing_url": "https://open.bigmodel.cn/",
        "local": False
    },
    # New providers from v1.4
    "openrouter": {
        "name": "OpenRouter",
        "models": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "google/gemini-pro-1.5", "meta-llama/llama-3.1-70b-instruct", "mistralai/mistral-large"],
        "default_model": "anthropic/claude-3.5-sonnet",
        "billing_url": "https://openrouter.ai/settings/keys",
        "local": False
    },
    "cerebras": {
        "name": "Cerebras",
        "models": ["llama-3.3-70b", "llama-3.1-70b", "mixtral-8x7b", "qwen-2.5-32b"],
        "default_model": "llama-3.3-70b",
        "billing_url": "https://cloud.cerebras.ai/",
        "local": False
    },
    "huggingface": {
        "name": "HuggingFace",
        "models": ["meta-llama/Llama-3.3-70B-Instruct", "Qwen/Qwen2.5-72B-Instruct", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
        "default_model": "meta-llama/Llama-3.3-70B-Instruct",
        "billing_url": "https://huggingface.io/settings/billing",
        "local": False
    },
    "kimi-coding": {
        "name": "Kimi Coding (Moonshot)",
        "models": ["kimi-coder-flash", "kimi-coder", "kimi-long"],
        "default_model": "kimi-coder-flash",
        "billing_url": "https://platform.moonshot.cn/",
        "local": False
    },
    "opencode": {
        "name": "OpenCode",
        "models": ["opencode", "opencode-32b", "opencode-8b"],
        "default_model": "opencode",
        "billing_url": "https://opencode.ai/",
        "local": False
    },
    "vercel-ai-gateway": {
        "name": "Vercel AI Gateway",
        "models": ["gpt-4o", "claude-3.5-sonnet", "gemini-1.5-pro"],
        "default_model": "gpt-4o",
        "billing_url": "https://vercel.com/dashboard/ai-gateway",
        "local": False
    }
}

# Encryption functions (matching CLI)
def get_master_key() -> bytes:
    """Get or create master encryption key"""
    if MASTER_KEY_FILE.exists():
        return MASTER_KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    MASTER_KEY_FILE.write_bytes(key)
    os.chmod(str(MASTER_KEY_FILE), 0o600)
    return key

def encrypt_key(key: str) -> str:
    """Encrypt an API key"""
    f = Fernet(get_master_key())
    return base64.b64encode(f.encrypt(key.encode())).decode()

def decrypt_key(encrypted: str) -> str:
    """Decrypt an API key"""
    f = Fernet(get_master_key())
    return f.decrypt(base64.b64decode(encrypted.encode())).decode()

def load_keys() -> dict:
    """Load encrypted keys"""
    if not KEYS_FILE.exists():
        return {}
    try:
        with open(KEYS_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys: dict):
    """Save encrypted keys"""
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)
    os.chmod(str(KEYS_FILE), 0o600)

def load_config() -> dict:
    """Load ClawAPI config"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {"selected_models": {}}

def save_config(config: dict):
    """Save ClawAPI config"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_openclaw_config() -> dict:
    """Get OpenClaw config"""
    if OPENCLAW_CONFIG.exists():
        with open(OPENCLAW_CONFIG) as f:
            return json.load(f)
    return {}

def update_openclaw_model(model: str):
    """Update OpenClaw default model"""
    if OPENCLAW_CONFIG.exists():
        with open(OPENCLAW_CONFIG) as f:
            config = json.load(f)
        config['defaultModel'] = model
        config['model'] = model
        with open(OPENCLAW_CONFIG, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    return False

def log_activity(message: str, level: str = "info"):
    """Log activity to file"""
    log_file = CONFIG_DIR / "activity.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} [{level.upper()}] {message}\n")

def get_activity_logs(limit: int = 50) -> list:
    """Get recent activity logs"""
    log_file = CONFIG_DIR / "activity.log"
    logs = []
    if log_file.exists():
        with open(log_file) as f:
            lines = f.readlines()[-limit:]
        for line in lines:
            parts = line.strip().split(']', 1)
            if len(parts) == 2:
                time_part = parts[0].replace('[', '')
                msg = parts[1].strip()
                level = "info"
                if '[' in msg:
                    msg_parts = msg.split(']', 1)
                    if len(msg_parts) == 2:
                        level = msg_parts[0].strip()
                        msg = msg_parts[1].strip()
                logs.append({'time': time_part, 'message': msg, 'level': level})
    return list(reversed(logs))

# HTML Template - Complete UI
HTML_TEMPLATE = r'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClawAPI Linux 🦆</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        header { 
            background: linear-gradient(135deg, rgba(79, 70, 229, 0.3), rgba(124, 58, 237, 0.2));
            padding: 20px 30px;
            border-radius: 16px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid rgba(79, 70, 229, 0.3);
        }
        .logo { display: flex; align-items: center; gap: 12px; }
        .logo h1 { font-size: 1.8rem; background: linear-gradient(135deg, #fff, #a5b4fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .logo-icon { font-size: 2rem; }
        .status-badge {
            background: linear-gradient(135deg, #00d26a, #00b558);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #000;
        }
        
        .nav { 
            display: flex; 
            gap: 8px;
            margin-bottom: 25px;
            background: rgba(255,255,255,0.05);
            padding: 6px;
            border-radius: 12px;
        }
        .nav a {
            padding: 12px 24px;
            background: transparent;
            border-radius: 8px;
            color: #a0a0a0;
            text-decoration: none;
            transition: all 0.2s;
            font-weight: 500;
        }
        .nav a:hover { background: rgba(255,255,255,0.1); color: #fff; }
        .nav a.active {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: #fff;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
        }
        
        .card {
            background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .card h2 { 
            margin-bottom: 20px; 
            font-size: 1.3rem; 
            display: flex; align-items: center; gap: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 25px;
        }
        .stat-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
            padding: 24px;
            border-radius: 14px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.06);
        }
        .stat-value { font-size: 2rem; font-weight: 700; color: #a5b4fc; }
        .stat-label { font-size: 0.9rem; color: #888; margin-top: 8px; }
        
        .providers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
        }
        .provider-card {
            background: rgba(255,255,255,0.04);
            border: 2px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 20px;
        }
        .provider-card.configured { border-color: rgba(0, 210, 106, 0.4); }
        
        .provider-header { display: flex; justify-content: space-between; margin-bottom: 15px; }
        .provider-name { font-weight: 600; font-size: 1.1rem; }
        .provider-status {
            font-size: 0.75rem;
            padding: 5px 10px;
            border-radius: 12px;
        }
        .status-configured { background: #00d26a; color: #000; }
        .status-missing { background: #666; color: #fff; }
        
        .provider-model { 
            background: rgba(79, 70, 229, 0.2); 
            padding: 8px 12px; 
            border-radius: 8px; 
            font-size: 0.85rem;
            margin: 10px 0;
        }
        
        .provider-actions { display: flex; gap: 8px; margin-top: 15px; }
        
        .btn {
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-flex;
            align-items: center; gap: 6px;
        }
        .btn-primary { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff; }
        .btn-danger { background: linear-gradient(135deg, #dc2626, #b91c1c); color: #fff; }
        .btn-success { background: linear-gradient(135deg, #00d26a, #00b558); color: #000; }
        .btn-secondary { background: rgba(255,255,255,0.1); color: #fff; }
        .btn-small { padding: 6px 12px; font-size: 0.8rem; }
        
        .form-group { margin-bottom: 18px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 500; }
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.15);
            background: rgba(255,255,255,0.08);
            color: #fff;
        }
        
        .current-model-display {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            padding: 30px;
            border-radius: 14px;
            text-align: center;
            margin-bottom: 25px;
        }
        .current-model-display h3 { opacity: 0.9; }
        .current-model-display .model-name { font-size: 2rem; font-weight: 700; margin-top: 8px; }
        
        .log-entry {
            padding: 14px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            display: flex; gap: 12px;
        }
        .log-time { color: #666; font-size: 0.8rem; min-width: 140px; }
        
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.85);
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        .modal.show { display: flex; }
        .modal-content {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            padding: 30px;
            border-radius: 16px;
            max-width: 450px;
            width: 90%;
        }
        .modal h3 { margin-bottom: 20px; }
        .modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; }
        
        .alert {
            padding: 14px 18px;
            border-radius: 10px;
            margin-bottom: 18px;
        }
        .alert-success { background: rgba(0,210,106,0.15); border: 1px solid #00d26a; color: #00d26a; }
        .alert-error { background: rgba(220,38,38,0.15); border: 1px solid #dc2626; color: #fca5a5; }
        
        .usage-card {
            background: rgba(255,255,255,0.04);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .usage-link { color: #4f46e5; text-decoration: none; }
        
        .settings-section { margin-bottom: 25px; }
        .settings-section h3 { margin-bottom: 15px; color: #aaa; font-size: 0.9rem; text-transform: uppercase; }
        .setting-row { 
            display: flex; justify-content: space-between;
            padding: 15px; background: rgba(255,255,255,0.03); border-radius: 10px; margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">
                <span class="logo-icon">🦆</span>
                <h1>ClawAPI Linux</h1>
            </div>
            <span class="status-badge">✓ Running</span>
        </header>
        
        <nav class="nav">
            <a href="/" class="{{ 'active' if page == 'dashboard' else '' }}">Dashboard</a>
            <a href="/providers" class="{{ 'active' if page == 'providers' else '' }}">Providers</a>
            <a href="/models" class="{{ 'active' if page == 'models' else '' }}">Models</a>
            <a href="/usage" class="{{ 'active' if page == 'usage' else '' }}">Usage</a>
            <a href="/activity" class="{{ 'active' if page == 'activity' else '' }}">Activity</a>
            <a href="/settings" class="{{ 'active' if page == 'settings' else '' }}">Settings</a>
        </nav>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% if page == 'dashboard' %}
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ configured_count }}/{{ total_providers }}</div>
                <div class="stat-label">Configured Providers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ openclaw_model }}</div>
                <div class="stat-label">Current Model</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ activity_count }}</div>
                <div class="stat-label">Activities Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">✓</div>
                <div class="stat-label">Keys Encrypted</div>
            </div>
        </div>
        
        <div class="card">
            <h2>⚡ Quick Actions</h2>
            <div style="display: flex; gap: 12px;">
                <a href="/providers" class="btn btn-primary">Manage Providers</a>
                <a href="/models" class="btn btn-primary">Switch Model</a>
                <a href="/settings" class="btn btn-secondary">Settings</a>
            </div>
        </div>
        
        <div class="card">
            <h2>📋 Recent Activity</h2>
            {% for log in recent_logs[:5] %}
            <div class="log-entry">
                <span class="log-time">{{ log.time }}</span>
                <span>{{ log.message }}</span>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if page == 'providers' %}
        <div class="card">
            <h2>🔑 API Providers</h2>
            <div class="providers-grid">
                {% for provider_id, provider in providers.items() %}
                <div class="provider-card {{ 'configured' if provider_id in configured_providers else '' }}">
                    <div class="provider-header">
                        <span class="provider-name">{{ provider.name }}</span>
                        <span class="provider-status {{ 'status-configured' if provider_id in configured_providers else 'status-missing' }}">
                            {{ 'Configured' if provider_id in configured_providers else 'Missing' }}
                        </span>
                    </div>
                    {% if provider_id in configured_providers %}
                    <div class="provider-model">Model: {{ selected_models.get(provider_id, provider.default_model) }}</div>
                    {% endif %}
                    <div class="provider-actions">
                        {% if provider_id in configured_providers %}
                        <form method="POST" action="/remove_key/{{ provider_id }}">
                            <button type="submit" class="btn btn-danger btn-small">Remove</button>
                        </form>
                        {% else %}
                        <button class="btn btn-primary btn-small" onclick="showAddModal('{{ provider_id }}', '{{ provider.name }}')">Add</button>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        {% if page == 'models' %}
        <div class="current-model-display">
            <h3>Current Model</h3>
            <div class="model-name">{{ openclaw_model }}</div>
        </div>
        
        <div class="card">
            <h2>🤖 Select Model</h2>
            <form method="POST" action="/set_model">
                <div class="form-group">
                    <label>Provider</label>
                    <select name="provider" required>
                        {% for provider_id in configured_providers %}
                        <option value="{{ provider_id }}">{{ providers[provider_id].name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>Model</label>
                    <input type="text" name="model" placeholder="e.g., gpt-4o, claude-sonnet-4-6" required>
                </div>
                <button type="submit" class="btn btn-primary">Set as Default</button>
            </form>
        </div>
        {% endif %}
        
        {% if page == 'usage' %}
        <div class="card">
            <h2>💰 Usage</h2>
            {% for provider_id in configured_providers %}
                {% if provider_id in providers and providers[provider_id].billing_url %}
                <div class="usage-card">
                    <div>
                        <strong>{{ providers[provider_id].name }}</strong>
                    </div>
                    <a href="{{ providers[provider_id].billing_url }}" target="_blank" class="usage-link">Open Dashboard →</a>
                </div>
                {% endif %}
            {% endfor %}
        </div>
        {% endif %}
        
        {% if page == 'activity' %}
        <div class="card">
            <h2>📝 Activity</h2>
            {% for log in logs %}
            <div class="log-entry">
                <span class="log-time">{{ log.time }}</span>
                <span>{{ log.message }}</span>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if page == 'settings' %}
        <div class="card">
            <h2>⚙️ Settings</h2>
            <div class="settings-section">
                <h3>OpenClaw</h3>
                <div class="setting-row">
                    <span>Config Path</span>
                    <code>{{ openclaw_config_path }}</code>
                </div>
                <div class="setting-row">
                    <span>Default Model</span>
                    <span>{{ openclaw_model }}</span>
                </div>
            </div>
            <div class="settings-section">
                <h3>Actions</h3>
                <div style="display: flex; gap: 12px;">
                    <form method="POST" action="/sync">
                        <button type="submit" class="btn btn-success">Sync to OpenClaw</button>
                    </form>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
    
    <div id="addModal" class="modal">
        <div class="modal-content">
            <h3 id="modalTitle">Add Provider</h3>
            <form method="POST" action="/add_key">
                <input type="hidden" name="provider" id="modalProvider">
                <div class="form-group">
                    <label>Model</label>
                    <input type="text" name="default_model" placeholder="Default model">
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="hideModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        function showAddModal(providerId, providerName) {
            document.getElementById('modalProvider').value = providerId;
            document.getElementById('modalTitle').textContent = 'Configure ' + providerName;
            document.getElementById('addModal').classList.add('show');
        }
        function hideModal() {
            document.getElementById('addModal').classList.remove('show');
        }
    </script>
</body>
</html>
'''

def get_configured_providers() -> list:
    """Get list of providers with saved keys"""
    keys = load_keys()
    config = load_config()
    providers = list(keys.keys())
    # Also include local providers like Ollama
    for p_id, p_data in PROVIDERS.items():
        if p_data.get('local') and p_id not in providers:
            providers.append(p_id)
    return providers

def get_selected_models() -> dict:
    """Get selected models per provider"""
    config = load_config()
    return config.get('selected_models', {})

def get_openclaw_model() -> str:
    """Get current OpenClaw default model"""
    config = get_openclaw_config()
    return config.get('defaultModel', config.get('model', 'Not set'))

@app.route('/')
def dashboard():
    configured = get_configured_providers()
    selected = get_selected_models()
    logs = get_activity_logs()
    today = datetime.now().strftime("%Y-%m-%d")
    today_logs = [l for l in logs if l['time'].startswith(today)]
    
    return render_template_string(HTML_TEMPLATE, 
        page='dashboard',
        providers=PROVIDERS,
        configured_providers=configured,
        selected_models=selected,
        configured_count=len(configured),
        total_providers=len(PROVIDERS),
        openclaw_model=get_openclaw_model(),
        activity_count=len(today_logs),
        recent_logs=logs,
        keys_secure=True,
        openclaw_config_path=str(OPENCLAW_CONFIG),
        keys_file=str(KEYS_FILE))

@app.route('/providers')
def providers_page():
    configured = get_configured_providers()
    selected = get_selected_models()
    return render_template_string(HTML_TEMPLATE,
        page='providers',
        providers=PROVIDERS,
        configured_providers=configured,
        selected_models=selected)

@app.route('/models')
def models_page():
    configured = get_configured_providers()
    return render_template_string(HTML_TEMPLATE,
        page='models',
        providers=PROVIDERS,
        configured_providers=configured,
        openclaw_model=get_openclaw_model())

@app.route('/usage')
def usage_page():
    configured = get_configured_providers()
    return render_template_string(HTML_TEMPLATE,
        page='usage',
        providers=PROVIDERS,
        configured_providers=configured)

@app.route('/activity')
def activity_page():
    logs = get_activity_logs()
    return render_template_string(HTML_TEMPLATE,
        page='activity',
        logs=logs)

@app.route('/settings')
def settings_page():
    return render_template_string(HTML_TEMPLATE,
        page='settings',
        openclaw_model=get_openclaw_model(),
        openclaw_config_path=str(OPENCLAW_CONFIG))

@app.route('/add_key', methods=['POST'])
def add_key():
    provider = request.form.get('provider')
    default_model = request.form.get('default_model', '')
    
    keys = load_keys()
    config = load_config()
    
    if provider in PROVIDERS:
        keys[provider] = "configured"  # Mark as configured
        if default_model:
            if 'selected_models' not in config:
                config['selected_models'] = {}
            config['selected_models'][provider] = default_model
        
        save_keys(keys)
        save_config(config)
        log_activity(f"Added provider: {PROVIDERS[provider]['name']}", "success")
        flash(f'Provider {PROVIDERS[provider]["name"]} configured!', 'success')
    
    return redirect('/providers')

@app.route('/remove_key/<provider>')
def remove_key(provider):
    keys = load_keys()
    config = load_config()
    
    if provider in keys:
        del keys[provider]
    if 'selected_models' in config and provider in config['selected_models']:
        del config['selected_models'][provider]
    
    save_keys(keys)
    save_config(config)
    log_activity(f"Removed provider: {PROVIDERS.get(provider, {}).get('name', provider)}", "info")
    flash('Provider removed', 'success')
    
    return redirect('/providers')

@app.route('/set_model', methods=['POST'])
def set_model():
    provider = request.form.get('provider')
    model = request.form.get('model')
    
    config = load_config()
    if 'selected_models' not in config:
        config['selected_models'] = {}
    config['selected_models'][provider] = model
    
    save_config(config)
    
    # Also update OpenClaw config
    if update_openclaw_model(model):
        log_activity(f"Set default model to {model} ({PROVIDERS.get(provider, {}).get('name', provider)})", "success")
        flash(f'Model set to {model}!', 'success')
    else:
        flash('Could not update OpenClaw config', 'error')
    
    return redirect('/models')

@app.route('/sync', methods=['POST'])
def sync_to_openclaw():
    config = load_config()
    selected = config.get('selected_models', {})
    
    if selected:
        # Set first selected model as default
        first_model = list(selected.values())[0]
        if update_openclaw_model(first_model):
            log_activity(f"Synced to OpenClaw: {first_model}", "success")
            flash(f'Synced model {first_model} to OpenClaw!', 'success')
        else:
            flash('OpenClaw config not found', 'error')
    else:
        flash('No models configured', 'error')
    
    return redirect('/settings')

@app.route('/reset', methods=['POST'])
def reset_all():
    global PROVIDERS
    save_keys({})
    save_config({"selected_models": {}})
    log_activity("Reset all settings", "info")
    flash('All settings reset', 'success')
    return redirect('/settings')

if __name__ == '__main__':
    log_activity("ClawAPI Linux Web UI started")
    print("🚀 ClawAPI Linux Web UI running at http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
