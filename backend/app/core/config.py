import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================
# LOAD BACKEND .env
# ============================================

BACKEND_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

ENV_FILE = (
    BACKEND_ROOT
    / ".env"
)

load_dotenv(ENV_FILE)


# ============================================
# FASTAPI
# ============================================

APP_NAME = "RetailEdge AI API"

APP_VERSION = "0.1.0"

API_V1_PREFIX = "/api/v1"


# ============================================
# CORS
# ============================================

raw_cors = os.getenv("CORS_ORIGINS", "")
if raw_cors:
    CORS_ORIGINS = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]
else:
    CORS_ORIGINS = ["*"]



# ============================================
# CLOUD SYNC
# ============================================

SUPABASE_INGEST_URL = os.getenv(
    "SUPABASE_INGEST_URL",
    ""
)


SUPABASE_HISTORY_URL = os.getenv(
    "SUPABASE_HISTORY_URL",
    ""
)


EDGE_INGEST_TOKEN = os.getenv(
    "EDGE_INGEST_TOKEN",
    ""
)


EDGE_DEVICE_ID = os.getenv(
    "EDGE_DEVICE_ID",
    "edge-01"
)


CLOUD_SYNC_ENABLED = (
    os.getenv(
        "CLOUD_SYNC_ENABLED",
        "false"
    ).lower()
    == "true"
)


CLOUD_SYNC_INTERVAL_SECONDS = int(
    os.getenv(
        "CLOUD_SYNC_INTERVAL_SECONDS",
        "10"
    )
)


CLOUD_SYNC_BATCH_SIZE = int(
    os.getenv(
        "CLOUD_SYNC_BATCH_SIZE",
        "20"
    )
)


# ============================================
# LOCAL SQLITE DATABASE
# ============================================

LOCAL_DB_PATH = (
    BACKEND_ROOT
    / "data"
    / "retailedge.db"
)