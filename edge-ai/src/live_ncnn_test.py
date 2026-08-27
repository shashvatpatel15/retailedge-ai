import cv2

from core.camera import (
    CameraStream
)

from detection.ncnn_person_detector import (
    NcnnPersonDetector
)


TEST_FRAMES = 30


def main():

    print()
    print(
        "Starting Raspberry Pi "
        "live NCNN person detection..."
    )
    print()


    # ==================================================
    # LOAD DETECTOR
    # ==================================================

    detector = (
        NcnnPersonDetector()
    )


    # ==================================================
    # START CAMERA
    # ==================================================

    camera = (
        CameraStream()
    )


    camera.start()


    inference_times = []

    last_frame = None


    print()
    print(
        "Live detection started."
    )
    print()


    # ==================================================
    # PROCESS FRAMES
    # ==================================================

    try:

        for frame_number in range(
            1,
            TEST_FRAMES + 1
        ):

            frame = (
                camera.read()
            )


            if frame is None:

                print(
                    "Frame unavailable."
                )

                continue


            (
                people,
                inference_time
            ) = detector.detect(
                frame
            )


            inference_times.append(
                inference_time
            )


            fps = (
                1
                /
                inference_time
            )


            print(
                f"Frame "
                f"{frame_number:02d}"
                f" | People: "
                f"{len(people)}"
                f" | Inference: "
                f"{inference_time:.3f}s"
                f" | AI FPS: "
                f"{fps:.2f}"
            )


            # ==========================================
            # DRAW DETECTIONS
            # ==========================================

            for person in people:

                (
                    x1,
                    y1,
                    x2,
                    y2
                ) = person[
                    "bbox"
                ]


                (
                    foot_x,
                    foot_y
                ) = person[
                    "foot"
                ]


                confidence = (
                    person[
                        "confidence"
                    ]
                )


                # Bounding box
                cv2.rectangle(
                    frame,
                    (
                        x1,
                        y1
                    ),
                    (
                        x2,
                        y2
                    ),
                    (
                        255,
                        255,
                        255
                    ),
                    2
                )


                # Person label
                cv2.putText(
                    frame,
                    (
                        f"Person "
                        f"{confidence:.2f}"
                    ),
                    (
                        x1,
                        max(
                            20,
                            y1 - 8
                        )
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (
                        255,
                        255,
                        255
                    ),
                    1
                )


                # Bottom-center tracking point
                cv2.circle(
                    frame,
                    (
                        foot_x,
                        foot_y
                    ),
                    4,
                    (
                        255,
                        255,
                        255
                    ),
                    -1
                )


            last_frame = (
                frame.copy()
            )


    except KeyboardInterrupt:

        print()
        print(
            "Detection stopped "
            "by user."
        )


    finally:

        camera.release()


    # ==================================================
    # SAVE FINAL FRAME
    # ==================================================

    if last_frame is not None:

        cv2.imwrite(
            "live_person_result.jpg",
            last_frame
        )


    # ==================================================
    # PERFORMANCE RESULT
    # ==================================================

    if inference_times:

        average_time = (
            sum(
                inference_times
            )
            /
            len(
                inference_times
            )
        )


        average_fps = (
            1
            /
            average_time
        )


        print()
        print(
            "================================"
        )

        print(
            "RPI 3 B+ LIVE NCNN RESULT"
        )

        print(
            "================================"
        )


        print(
            f"Frames processed: "
            f"{len(inference_times)}"
        )


        print(
            f"Average inference: "
            f"{average_time:.3f}s"
        )


        print(
            f"Average AI FPS: "
            f"{average_fps:.2f}"
        )


        print(
            "Saved result: "
            "live_person_result.jpg"
        )


        print(
            "================================"
        )


if __name__ == "__main__":

    main()