#!/bin/bash
# Publish nexaclient Python package v1.2.0 to PyPI

echo "🚀 Publishing nexaclient v1.2.0 to PyPI..."
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
echo "✅ Done! Verify at: https://pypi.org/project/nexaclient/"
echo ""
echo "Test installation:"
echo "  pip install --upgrade nexaclient"
echo "  python3 -c 'from nexaclient import NexaClient; print(NexaClient.__doc__)'"
