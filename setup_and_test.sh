#!/bin/bash

# Fast Inference Server - Complete Setup and Test Script
# This script will set up everything and run a complete test

set -e

echo "=========================================="
echo "Fast Inference Server - Complete Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
print_info "Python version: $python_version"

# Step 2: Create virtual environment
echo ""
echo "Step 2: Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Step 3: Activate virtual environment
echo ""
echo "Step 3: Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Step 4: Install dependencies
echo ""
echo "Step 4: Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
print_success "Dependencies installed"

# Step 5: Verify installation
echo ""
echo "Step 5: Verifying installation..."
python verify_installation.py
if [ $? -eq 0 ]; then
    print_success "Installation verified"
else
    print_error "Installation verification failed"
    exit 1
fi

# Step 6: Test serialization
echo ""
echo "Step 6: Testing binary protocol..."
python binary_protocol.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Binary protocol test passed"
else
    print_error "Binary protocol test failed"
    exit 1
fi

# Step 7: Run benchmark (without server)
echo ""
echo "Step 7: Running serialization benchmark..."
python -c "
from binary_protocol import dict_to_binary, binary_to_dict
import numpy as np
import time

data = {
    'state': np.random.randn(10).astype(np.float32),
    'image': np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
}

start = time.time()
binary = dict_to_binary(data)
t1 = time.time() - start

start = time.time()
restored = binary_to_dict(binary)
t2 = time.time() - start

print(f'Serialize: {t1*1000:.2f} ms, Deserialize: {t2*1000:.2f} ms')
print(f'Data size: {len(binary)/1024:.2f} KB')
"
print_success "Benchmark completed"

# Step 8: Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the server:"
echo "   python server.py --model-path /path/to/model --device cpu --port 50000"
echo ""
echo "2. In another terminal, test the server:"
echo "   python test_server.py"
echo ""
echo "3. Run comprehensive benchmark:"
echo "   python benchmark.py"
echo ""
echo "4. Try the examples:"
echo "   python example_usage.py"
echo ""
echo "For more information:"
echo "  - README.md: Project overview"
echo "  - DEVELOPMENT.md: Development guide"
echo "  - FAQ.md: Frequently asked questions"
echo ""
print_success "All setup steps completed successfully!"
echo ""
