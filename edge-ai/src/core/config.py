import os
from pathlib import Path
from dotenv import load_dotenv


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

BACKEND_ENV = (
    PROJECT_ROOT
    / "backend"
    / ".env"
)

if BACKEND_ENV.exists():
    load_dotenv(BACKEND_ENV)


# CAMERA

CAMERA_SOURCE = os.getenv(
    "CAMERA_SOURCE",
    "http://127.0.0.1:8080/video"
)

FRAME_WIDTH = 640
FRAME_HEIGHT = 480


# YOLO

YOLO_MODEL = os.getenv(
    "YOLO_MODEL",
    "yolo11n.pt"
)

YOLO_IMAGE_SIZE = int(
    os.getenv(
        "YOLO_IMAGE_SIZE",
        "640"
    )
)

PERSON_CLASS_ID = 0

PERSON_CONFIDENCE = float(
    os.getenv(
        "PERSON_CONFIDENCE",
        "0.40"
    )
)


# QUEUE

QUEUE_ZONE = (
    300,
    120,
    630,
    470
)

QUEUE_CONFIRM_TIME = 1.0

QUEUE_EXIT_GRACE = 1.5

QUEUE_LENGTH_THRESHOLD = 3

WAIT_TIME_THRESHOLD = 5.0

TRACK_TIMEOUT = 2.0