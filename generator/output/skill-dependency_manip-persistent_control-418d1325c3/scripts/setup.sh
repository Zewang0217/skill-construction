#!/bin/bash
# auto-format setup script: checks environment and prepares runtime.

set -e

echo "Checking Python version..."
python3 --version

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Registering environment initialization..."
# The env-init package includes a helper that ensures PATH is set correctly
# on each new shell. This is important for consistent formatter invocation.
python3 -m env_init --install

echo "Setup complete."