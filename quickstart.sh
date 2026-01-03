#!/bin/bash

echo "=================================="
echo "Wedding Venue Finder - Quick Start"
echo "=================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "1. Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "2. Initializing database with venues..."
python3 seed_data.py

echo ""
echo "=================================="
echo "Setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "  CLI Interface:"
echo "    python3 cli.py list"
echo "    python3 cli.py view 1"
echo ""
echo "  Web Interface:"
echo "    python3 web.py"
echo "    Then open: http://127.0.0.1:5000"
echo ""
echo "  See README.md for full documentation"
echo ""
