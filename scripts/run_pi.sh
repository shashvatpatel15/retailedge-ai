#!/bin/bash
# ==============================================================================
# RetailEdge AI - Raspberry Pi 3 B+ Launcher Script
# ==============================================================================
set -e

# Change to project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Activate or create virtualenv
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment (.venv)..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Ensure required packages are installed inside the virtualenv
if ! python3 -c "import uvicorn, fastapi, ncnn, cv2" &>/dev/null; then
    echo "Installing/verifying lightweight dependencies (requirements-pi.txt)..."
    pip install --upgrade pip
    pip install -r requirements-pi.txt
fi

# Set Python search path
export PYTHONPATH="$PROJECT_ROOT/backend:$PROJECT_ROOT/edge-ai/src:$PYTHONPATH"

# Set Pi 3 B+ optimized environment variables
export DETECTOR_BACKEND="ncnn"
export YOLO_MODEL="yolo11n_ncnn_model"
export YOLO_IMAGE_SIZE="320"
export NCNN_NUM_THREADS="4"
export ALLOW_MOCK_CAMERA="true"

# Handle arguments
if [ "$1" = "backend" ] || [ "$1" = "api" ]; then
    shift || true
    echo "Starting RetailEdge FastAPI backend on 0.0.0.0:8000..."
    exec python3 -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 "$@"
else
    echo "Starting Standalone RetailEdge AI Queue Monitor..."
    exec python3 edge-ai/src/run_queue_pi.py "$@"
fi
