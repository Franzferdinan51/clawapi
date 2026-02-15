#!/bin/bash
# ClawAPI Linux Installer

INSTALL_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/clawapi"

echo "Installing ClawAPI Linux..."

# Create install directory
mkdir -p "$INSTALL_DIR"

# Copy the script
cp "$(dirname "$0")/clawapi-linux.py" "$INSTALL_DIR/clawapi-linux"
chmod +x "$INSTALL_DIR/clawapi-linux"

# Create symlink for easy access
ln -sf "$INSTALL_DIR/clawapi-linux" "$INSTALL_DIR/clawapi" 2>/dev/null

echo "✓ Installed to $INSTALL_DIR/clawapi-linux"
echo ""
echo "Usage:"
echo "  clawapi-linux list                    # List providers"
echo "  clawapi-linux add openai sk-xxx      # Add API key"
echo "  clawapi-linux models anthropic        # List models"
echo "  clawapi-linux set openai gpt-4o       # Set default model"
echo ""
echo "Make sure $INSTALL_DIR is in your PATH!"
