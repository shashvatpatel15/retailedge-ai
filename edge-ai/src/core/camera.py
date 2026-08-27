import cv2

from core.config import (
    CAMERA_SOURCE,
    FRAME_WIDTH,
    FRAME_HEIGHT
)


class CameraStream:

    def __init__(self, source=None):
        raw_source = source if source is not None else CAMERA_SOURCE

        # If source is a digit string (e.g. "0" or "1"), convert to integer index
        if isinstance(raw_source, str) and raw_source.isdigit():
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

        if not self.cap.isOpened():
            raise RuntimeError(f"Could not connect to camera source: {self.source}")

    def read(self):
        if not self.cap.isOpened():
            return None

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
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()