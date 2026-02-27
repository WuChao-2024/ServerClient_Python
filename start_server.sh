#!/bin/bash

# Fast Inference Server - Quick Start Script
# This script helps you quickly set up and run the server

set -e

echo "=========================================="
echo "Fast Inference Server - Quick Start"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if Python >= 3.8
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Check if model path is provided
echo ""
echo "=========================================="
echo "Server Configuration"
echo "=========================================="
echo ""

read -p "Enter model path (or press Enter to use dummy model): " model_path
if [ -z "$model_path" ]; then
    model_path="./dummy_model"
    echo "Using dummy model for testing"
fi

read -p "Enter device (cpu/cuda:0) [default: cpu]: " device
device=${device:-cpu}

read -p "Enter port [default: 50000]: " port
port=${port:-50000}

echo ""
echo "Configuration:"
echo "  Model path: $model_path"
echo "  Device: $device"
echo "  Port: $port"
echo ""

# Start server
echo "=========================================="
echo "Starting server..."
echo "=========================================="
echo ""
echo "Server will be available at: http://127.0.0.1:$port"
echo "Press Ctrl+C to stop the server"
echo ""

python server.py --model-path "$model_path" --device "$device" --port "$port"
