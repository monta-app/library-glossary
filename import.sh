#!/bin/bash

# Monta Glossary Import Script Wrapper
# This script automatically activates the virtual environment and runs the import

set -e  # Exit on error

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run import
# Amendments, alternatives, and plurals are always applied automatically
source .venv/bin/activate
python import.py "$@"
