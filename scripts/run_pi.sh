#!/bin/bash
# ==============================================================================
# RetailEdge AI - Raspberry Pi 3 B+ Launcher Script
# ==============================================================================
set -e

# Activate virtualenv if available
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set Pi 3 B+ optimized environment variables
export DETECTOR_BACKEND="ncnn"
export YOLO_MODEL="yolo11n_ncnn_model"
export YOLO_IMAGE_SIZE="320"
export NCNN_NUM_THREADS="4"
export ALLOW_MOCK_CAMERA="true"

# Handle arguments
if [ "$1" = "backend" ] || [ "$1" = "api" ]; then
    echo "Starting RetailEdge FastAPI backend on 0.0.0.0:8000..."
    exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
else
    echo "Starting Standalone RetailEdge AI Queue Monitor..."
    exec python3 edge-ai/src/run_queue_pi.py "$@"
fi
