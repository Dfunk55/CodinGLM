#!/bin/bash
# Setup script for CodinGLM

set -e

echo "Setting up CodinGLM..."

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "Error: pip not found. Please install Python 3.10+ first."
    exit 1
fi

# Install in development mode
echo "Installing dependencies..."
pip install -e .

# Create example config if it doesn't exist
if [ ! -f "$HOME/.codinglm.json" ]; then
    echo "Creating example configuration at ~/.codinglm.json"
    cp .codinglm.json.example "$HOME/.codinglm.json"
    echo "Please edit ~/.codinglm.json and add your Z.ai API key"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit ~/.codinglm.json and add your Z.ai API key"
echo "2. Or set Z_AI_API_KEY environment variable"
echo "3. Run: codinglm"
echo ""
