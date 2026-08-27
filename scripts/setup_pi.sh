#!/bin/bash
# ==============================================================================
# RetailEdge AI - Raspberry Pi 3 B+ Automated Setup Script
# ==============================================================================
set -e

echo "=================================================="
echo "  Setting up RetailEdge AI on Raspberry Pi 3 B+  "
echo "=================================================="

# 1. Expand Swap Memory (Crucial for 1GB RAM Pi 3 B+)
if [ -f /etc/dphys-swapfile ]; then
    echo "[1/4] Checking and expanding swap memory to 1024MB..."
    sudo dphys-swapfile swapoff || true
    sudo sed -i 's/^CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
    echo "Swap size set to 1024MB."
else
    echo "[1/4] /etc/dphys-swapfile not found; skipping automatic swap resize."
fi

# 2. Install System Dependencies for OpenCV and NCNN OpenMP
echo "[2/4] Installing system packages..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    libgomp1 \
    libatlas-base-dev \
    libopenblas-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev

# 3. Create Python Virtual Environment
echo "[3/4] Creating Python virtual environment (.venv)..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip setuptools wheel

# 4. Install Lightweight Edge AI Dependencies
echo "[4/4] Installing lightweight Python requirements..."
pip install -r requirements-pi.txt

echo ""
echo "=================================================="
echo "  RetailEdge AI Pi 3 B+ Setup Complete! 🚀       "
echo "=================================================="
echo "To run the standalone Edge Queue monitor:"
echo "  source .venv/bin/activate"
echo "  python3 edge-ai/src/run_queue_pi.py"
echo ""
echo "To run the full FastAPI backend with Edge AI:"
echo "  source .venv/bin/activate"
echo "  uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"
echo "=================================================="
