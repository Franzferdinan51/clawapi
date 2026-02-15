#!/bin/bash
# ClawAPI Installer - Cross-platform
# Usage: ./install.sh

set -e

OS=$(uname -s | tr '[:upper:]' '[:lower:]')

echo "🦆 Installing ClawAPI for $OS..."

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install flask cryptography requests -q

# Make CLI executable
chmod +x clawapi.py

# Install CLI globally (optional)
if [ "$OS" = "linux" ]; then
    sudo cp clawapi.py /usr/local/bin/clawapi
    echo "✓ Installed to /usr/local/bin/clawapi"
elif [ "$OS" = "darwin" ]; then
    sudo cp clawapi.py /usr/local/bin/clawapi
    echo "✓ Installed to /usr/local/bin/clawapi"
elif [[ "$OS" == *"mingw"* ]] || [[ "$OS" == *"cygwin"* ]]; then
    echo "On Windows, add this folder to PATH"
fi

echo "✓ Installation complete!"
echo ""
echo "Usage:"
echo "  ./clawapi.py list                    # List providers"
echo "  ./clawapi.py add openai sk-xxx...   # Add API key"
echo "  ./clawapi.py models openai           # List models"
echo "  ./clawapi.py set openai gpt-4o      # Set default model"
echo "  ./clawapi.py show openai            # Show masked key"
echo "  ./clawapi.py remove openai          # Remove provider"
echo ""
echo "Web UI:"
echo "  source .venv/bin/activate"
echo "  python webui.py"
echo "  # Then open http://localhost:5001"
