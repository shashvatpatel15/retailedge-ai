# RetailEdge AI 🛒⚡

> **Real-Time Edge Computer Vision & Smart Billing Queue Analytics for Modern Retail**

RetailEdge AI is an intelligent edge-computing platform designed to monitor retail checkout lines, prevent bottlenecking, estimate customer wait times, and seamlessly synchronize store analytics to the cloud—even with intermittent network connectivity.

---

## 🌟 Key Features

- **Edge Computer Vision & Tracking**:
  - Person detection powered by **YOLO11** (`yolo11n.pt`).
  - Robust multi-object tracking via **ByteTrack** with footprint floor coordinate projection.
  - Configurable Region of Interest (ROI) queue zones with entry/exit stability filters.
- **Resilient FastAPI Backend**:
  - Thread-safe background execution of the Edge AI engine.
  - Local **SQLite** fallback database for offline-first data buffering.
  - Automated background batch synchronization worker pushing telemetry to Supabase.
- **Modern Live Dashboard**:
  - Built with **React**, **Vite**, and **Recharts**.
  - Real-time queue metrics: active queue count, average wait time, and congestion alerts.
  - Historical queue trends and edge device health diagnostics.

---

## 🏗️ Architecture Overview

```
 [ RTSP / IP Camera / Webcam ]
               │
               ▼
   [ Edge AI Vision Engine ]
   (YOLO11 + ByteTrack + ROI Analyzer)
               │
               ▼
    [ FastAPI Backend API ]
    ├── Live In-Memory State
    ├── Local SQLite Buffer (retailedge.db)
    └── Background Cloud Sync Worker
         │                     │
         ▼                     ▼
 [ React Dashboard ]   [ Supabase Cloud Edge Functions ]
 (Local In-Store UI)   (Central Analytics & Alerts)
```

---

## 📁 Repository Structure

```
retailedge-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # API routes (queue, health, history)
│   │   ├── core/             # App configuration, lifespans
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── services/         # Edge runner, cloud sync, local SQLite
│   │   ├── state/            # Thread-safe in-memory application state
│   │   └── main.py           # FastAPI entry point
│   ├── data/                 # Local database storage (.sqlite/.db)
│   ├── .env.example          # Backend environment variables template
│   └── requirements.txt      # Backend Python dependencies
├── edge-ai/
│   ├── src/
│   │   ├── analytics/        # Queue stability & wait-time analyzer
│   │   ├── core/             # Camera stream reader & video configs
│   │   ├── engine/           # QueueEngine processing loop
│   │   ├── tracking/         # YOLO + ByteTrack tracker
│   │   └── run_queue.py      # Standalone edge test runner
│   └── requirements.txt      # Vision & deep learning dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # UI cards, charts, and header widgets
│   │   ├── pages/            # Dashboard views
│   │   └── services/         # API client hooks
│   ├── package.json          # Node dependencies & scripts
│   └── vite.config.js        # Vite build configuration
├── .env.example              # Root environment template
├── .gitignore                # Comprehensive gitignore
├── requirements.txt          # Unified Python dependencies
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites

- **Python 3.10+**
- **Node.js 18+** & **npm**
- Camera source (Webcam, RTSP stream, or IP camera URL)

---

### 2. Environment Configuration

Copy the example environment configuration into `backend/.env`:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your deployment settings:

```env
SUPABASE_INGEST_URL=https://your-project.supabase.co/functions/v1/clever-handler
SUPABASE_HISTORY_URL=https://your-project.supabase.co/functions/v1/queue-history
EDGE_INGEST_TOKEN=your_token_here
EDGE_DEVICE_ID=edge-01
CLOUD_SYNC_ENABLED=false
CLOUD_SYNC_INTERVAL_SECONDS=10
CLOUD_SYNC_BATCH_SIZE=20
```

---

### 3. Backend & Edge AI Setup

Create and activate a Python virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Or activate on Linux/macOS
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Run the backend server (FastAPI):

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

> **API Documentation**: Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

---

### 4. Frontend Setup

Open a new terminal, navigate to `frontend/`, install dependencies, and start the development server:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser to view the live dashboard.

---

### 5. Running Standalone Edge Vision (Testing)

If you wish to test the YOLO vision tracking directly with a visual window:

```bash
python edge-ai/src/run_queue.py
```

---

## ⚙️ Edge AI Configuration

You can fine-tune camera feeds, detection thresholds, and queue zones in [`edge-ai/src/core/config.py`](edge-ai/src/core/config.py):

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `CAMERA_SOURCE` | `"0"` or stream URL | Camera device index or RTSP/HTTP URL |
| `YOLO_MODEL` | `"yolo11n.pt"` | YOLO model weights (auto-downloaded by Ultralytics) |
| `PERSON_CONFIDENCE` | `0.40` | Minimum detection confidence score |
| `QUEUE_ZONE` | `(300, 120, 630, 470)` | Coordinates `(x1, y1, x2, y2)` for the queue ROI |
| `QUEUE_CONFIRM_TIME` | `1.0s` | Time a person must remain in ROI to be counted |
| `QUEUE_LENGTH_THRESHOLD` | `3` | Number of people in queue to trigger high-congestion alert |

---

## 🛡️ License

This project is open source and available under the [MIT License](LICENSE).