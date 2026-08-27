import os
from pathlib import Path
from dotenv import load_dotenv


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

# Load root and backend .env files
ROOT_ENV = PROJECT_ROOT / ".env"
BACKEND_ENV = PROJECT_ROOT / "backend" / ".env"

if ROOT_ENV.exists():
    load_dotenv(ROOT_ENV)

if BACKEND_ENV.exists():
    load_dotenv(BACKEND_ENV)


# CAMERA CONFIGURATION
CAMERA_SOURCE = os.getenv(
    "CAMERA_SOURCE",
    "0"
)

FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "640"))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "480"))


# DETECTOR & MODEL SELECTION
NCNN_MODEL_DEFAULT = PROJECT_ROOT / "yolo11n_ncnn_model"
HAS_NCNN_MODEL = NCNN_MODEL_DEFAULT.exists()

# Backend can be "ncnn", "yolo", or "auto"
DETECTOR_BACKEND = os.getenv(
    "DETECTOR_BACKEND",
    "ncnn" if HAS_NCNN_MODEL else "yolo"
).lower()

if DETECTOR_BACKEND == "ncnn":
    YOLO_MODEL = os.getenv(
        "YOLO_MODEL",
        str(NCNN_MODEL_DEFAULT if HAS_NCNN_MODEL else "yolo11n_ncnn_model")
    )
    DEFAULT_IMG_SIZE = "320"
else:
    YOLO_MODEL = os.getenv(
        "YOLO_MODEL",
        "yolo11n.pt"
    )
    DEFAULT_IMG_SIZE = "640"

YOLO_IMAGE_SIZE = int(
    os.getenv(
        "YOLO_IMAGE_SIZE",
        DEFAULT_IMG_SIZE
    )
)

NCNN_NUM_THREADS = int(
    os.getenv(
        "NCNN_NUM_THREADS",
        "4"
    )
)

FRAME_SKIP = int(
    os.getenv(
        "FRAME_SKIP",
        "0"
    )
)

PERSON_CLASS_ID = 0

PERSON_CONFIDENCE = float(
    os.getenv(
        "PERSON_CONFIDENCE",
        "0.40"
    )
)


# BILLING QUEUE BUSINESS LOGIC
QUEUE_ZONE = (
    300,
    120,
    630,
    470
)

QUEUE_CONFIRM_TIME = float(os.getenv("QUEUE_CONFIRM_TIME", "1.0"))
QUEUE_EXIT_GRACE = float(os.getenv("QUEUE_EXIT_GRACE", "1.5"))
QUEUE_LENGTH_THRESHOLD = int(os.getenv("QUEUE_LENGTH_THRESHOLD", "3"))
WAIT_TIME_THRESHOLD = float(os.getenv("WAIT_TIME_THRESHOLD", "5.0"))
TRACK_TIMEOUT = float(os.getenv("TRACK_TIMEOUT", "2.0"))