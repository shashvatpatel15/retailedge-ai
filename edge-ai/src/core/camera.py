import os
import time
from pathlib import Path
import cv2
import numpy as np

from core.config import (
    CAMERA_SOURCE,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    PROJECT_ROOT
)


class MockCameraStream:
    """
    Simulated camera stream for testing queue processing when no physical camera is attached.
    Generates synthetic frames with simulated moving people in/out of the queue zone.
    """

    def __init__(self):
        print("Initialized Mock Camera Stream (Simulated retail environment).")
        self.frame_idx = 0

    def read(self):
        self.frame_idx += 1
        frame = np.full((FRAME_HEIGHT, FRAME_WIDTH, 3), 40, dtype=np.uint8)

        # Draw simulated store background
        cv2.line(frame, (0, 100), (FRAME_WIDTH, 100), (80, 80, 80), 2)
        cv2.putText(
            frame,
            "SIMULATED CAMERA FEED (No physical camera detected)",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (180, 180, 180),
            1
        )

        # Add simulated timestamp
        cv2.putText(
            frame,
            time.strftime("%Y-%m-%d %H:%M:%S"),
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 0),
            1
        )

        time.sleep(0.03)  # ~30fps rate limiting
        return frame

    def release(self):
        pass


class CameraStream:

    def __init__(self, source=None):
        raw_source = source if source is not None else CAMERA_SOURCE
        self.is_mock = False
        self.is_file = False
        self.mock_stream = None

        if str(raw_source).lower() in ("mock", "synthetic", "test"):
            self.is_mock = True
            self.mock_stream = MockCameraStream()
            return

        # Check if source is a file
        candidate_file = Path(raw_source)
        if not candidate_file.is_absolute():
            candidate_file = PROJECT_ROOT / raw_source

        if candidate_file.exists() and candidate_file.is_file():
            self.source = str(candidate_file)
            self.is_file = True
        elif isinstance(raw_source, str) and raw_source.isdigit():
            self.source = int(raw_source)
        else:
            self.source = raw_source

        print(f"Opening camera source: {self.source}")
        self.cap = cv2.VideoCapture(self.source)

        # Set small buffer size on edge devices to avoid frame buildup lag
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        # If primary integer device failed, attempt auto-scanning other V4L2 indices
        if not self.cap.isOpened() and isinstance(self.source, int):
            print(f"Index {self.source} unavailable. Scanning for other video capture devices...")
            for alt_idx in [1, 2, 3, 4, 10]:
                test_cap = cv2.VideoCapture(alt_idx)
                if test_cap.isOpened():
                    ret, _ = test_cap.read()
                    if ret:
                        print(f"Found active camera on /dev/video{alt_idx}!")
                        self.cap = test_cap
                        self.source = alt_idx
                        break
                test_cap.release()

        # Fallback to mock stream if no physical camera found and ALLOW_MOCK is enabled
        if not self.cap.isOpened():
            allow_mock = os.getenv("ALLOW_MOCK_CAMERA", "true").lower() in ("true", "1", "yes")
            if allow_mock:
                print("\n[WARNING] Could not open physical camera.")
                print("[FALLBACK] Starting Mock Camera Stream so AI queue engine continues running.")
                print("Tip: Set CAMERA_SOURCE=http://<PHONE_IP>:8080/video or connect a USB camera.\n")
                self.is_mock = True
                self.mock_stream = MockCameraStream()
                return

            raise RuntimeError(
                f"Could not connect to camera source: {self.source}. "
                f"Please verify camera connection or set CAMERA_SOURCE to an IP stream URL / video file."
            )

    def read(self):
        if self.is_mock:
            return self.mock_stream.read()

        if not self.cap.isOpened():
            return None

        success, frame = self.cap.read()

        # If video file reached EOF, loop back to the beginning
        if not success and self.is_file:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = self.cap.read()

        if not success or frame is None:
            return None

        # Resize to standard frame dimensions if necessary
        if frame.shape[1] != FRAME_WIDTH or frame.shape[0] != FRAME_HEIGHT:
            frame = cv2.resize(
                frame,
                (FRAME_WIDTH, FRAME_HEIGHT),
                interpolation=cv2.INTER_LINEAR
            )

        return frame

    def release(self):
        if self.is_mock:
            self.mock_stream.release()
        elif self.cap is not None and self.cap.isOpened():
            self.cap.release()