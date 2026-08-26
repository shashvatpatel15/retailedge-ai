import cv2

from core.config import (
    CAMERA_SOURCE,
    FRAME_WIDTH,
    FRAME_HEIGHT
)


class CameraStream:

    def __init__(self):

        self.cap = cv2.VideoCapture(
            CAMERA_SOURCE
        )

        if not self.cap.isOpened():

            raise RuntimeError(
                "Could not connect to camera."
            )


    def read(self):

        success, frame = self.cap.read()

        if not success:

            return None

        frame = cv2.resize(
            frame,
            (
                FRAME_WIDTH,
                FRAME_HEIGHT
            )
        )

        return frame


    def release(self):

        self.cap.release()