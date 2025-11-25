#!/bin/bash
# Publish nexadb Python package v1.1.0 to PyPI

echo "🚀 Publishing nexadb v1.1.0 to PyPI..."
echo ""

# Activate virtual environment
source .venv/bin/activate

# Install/upgrade twine
echo "📦 Installing twine..."
pip install --upgrade twine

# Upload to PyPI
echo ""
echo "📤 Uploading to PyPI..."
twine upload dist/*

echo ""
echo "✅ Done! Verify at: https://pypi.org/project/nexadb/"
echo ""
echo "Test installation:"
echo "  pip install --upgrade nexadb"
echo "  python3 -c 'from nexadb import NexaClient; print(NexaClient.__doc__)'"
