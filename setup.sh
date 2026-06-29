#!/bin/bash

echo "🔐 SC-Generator Setup"
echo "===================="
echo ""

# Check Python
echo "✓ Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found Python $PYTHON_VERSION"

# Check Node.js
echo "✓ Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "✗ Node.js not found. Please install Node.js 16+"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "  Found Node.js $NODE_VERSION"

# Create Python virtual environment
echo ""
echo "✓ Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "✓ Installing Python dependencies..."
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "  ✓ Python packages installed"
else
    echo "  ✗ Failed to install Python packages"
    exit 1
fi

# Install Node dependencies
echo "✓ Installing Node.js dependencies..."
npm install -q

if [ $? -eq 0 ]; then
    echo "  ✓ Node packages installed"
else
    echo "  ✗ Failed to install Node packages"
    exit 1
fi

# Create necessary directories
echo "✓ Creating directories..."
mkdir -p /tmp/sc-uploads
mkdir -p /tmp/sc-outputs
mkdir -p /tmp/sc-fingerprints

echo ""
echo "✓ Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Start the backend: python3 app.py"
echo "  2. Start the frontend: npm start"
echo ""
echo "Access the UI at: http://localhost:3000"
echo ""
