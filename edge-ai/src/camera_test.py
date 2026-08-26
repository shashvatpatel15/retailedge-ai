import cv2
import time

from core.config import CAMERA_SOURCE


def main():

    print("Connecting to camera...")

    cap = cv2.VideoCapture(
        CAMERA_SOURCE
    )

    if not cap.isOpened():
        raise RuntimeError(
            "Could not connect to camera."
        )

    print("Camera connected.")

    start_time = time.time()

    frame_count = 0

    while frame_count < 100:

        success, frame = cap.read()

        if not success:
            continue

        frame_count += 1

        if frame_count == 1:
            cv2.imwrite(
                "camera_test.jpg",
                frame
            )

        if frame_count % 20 == 0:

            elapsed = (
                time.time()
                - start_time
            )

            fps = (
                frame_count
                / elapsed
            )

            print(
                f"Frames: {frame_count}"
                f" | FPS: {fps:.2f}"
            )

    cap.release()

    elapsed = (
        time.time()
        - start_time
    )

    print(
        f"Average FPS: "
        f"{frame_count / elapsed:.2f}"
    )


if __name__ == "__main__":
    main()