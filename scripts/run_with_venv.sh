#!/bin/bash
# Activate the virtual environment and run commands with the correct Python

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Python executable path
PYTHON_PATH="$PROJECT_ROOT/.venv/bin/python"

# Check if virtual environment exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Virtual environment not found at $PYTHON_PATH"
    echo "🔧 Please run: python3 -m venv .venv && pip install -r requirements.txt"
    exit 1
fi

echo "🐍 Using Python: $PYTHON_PATH"

# Run the command with the virtual environment Python
exec "$PYTHON_PATH" "$@"
