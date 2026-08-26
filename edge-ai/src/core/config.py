# ============================================
# CAMERA
# ============================================

CAMERA_SOURCE = "http://10.77.77.63:8080/video"

FRAME_WIDTH = 640
FRAME_HEIGHT = 480


# ============================================
# YOLO
# ============================================

YOLO_MODEL = "yolo11n.pt"

PERSON_CLASS_ID = 0

PERSON_CONFIDENCE = 0.40


# ============================================
# QUEUE ZONE
# x1, y1, x2, y2
# ============================================

QUEUE_ZONE = (
    300,
    120,
    630,
    470
)


# ============================================
# QUEUE STABILITY
# ============================================

# Person must stay inside ROI this long
# before being counted as queue customer.
QUEUE_CONFIRM_TIME = 1.0


# Person may briefly leave ROI without
# immediately being removed from queue.
QUEUE_EXIT_GRACE = 1.5


# ============================================
# QUEUE ALERT
# ============================================

QUEUE_LENGTH_THRESHOLD = 3

WAIT_TIME_THRESHOLD = 5.0


# ============================================
# TRACKING
# ============================================

TRACK_TIMEOUT = 2.0