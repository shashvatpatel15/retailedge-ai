import cv2
import time
import threading
from copy import deepcopy

from core.camera import CameraStream

from core.config import (
    FRAME_WIDTH,
    QUEUE_ZONE
)

from tracking.yolo_bytetrack import PersonTracker
from analytics.queue_analyzer import QueueAnalyzer


class QueueEngine:

    def __init__(self):

        print("================================")
        print("RetailEdge AI")
        print("Smart Queue Monitoring Engine")
        print("================================")

        # Camera
        self.camera = CameraStream()

        # YOLO + ByteTrack
        self.tracker = PersonTracker()

        # Queue business logic
        self.queue_analyzer = QueueAnalyzer()

        # Thread-safe shared queue state
        self.snapshot_lock = threading.Lock()

        self.latest_snapshot = {
            "timestamp": time.time(),
            "tracked_people": 0,
            "queue_length": 0,
            "average_wait": 0.0,
            "longest_wait": 0.0,
            "alert": False
        }

        self.running = False

        self.last_error = None


    # ==================================================
    # GET CURRENT QUEUE STATE
    # ==================================================

    def get_snapshot(self):

        with self.snapshot_lock:

            return deepcopy(
                self.latest_snapshot
            )


    # ==================================================
    # STOP ENGINE
    # ==================================================

    def stop(self):

        self.running = False


    # ==================================================
    # UPDATE SHARED STATE
    # ==================================================

    def update_snapshot(
        self,
        people,
        queue_data
    ):

        snapshot = {

            "timestamp":
                time.time(),

            "tracked_people":
                len(people),

            "queue_length":
                queue_data[
                    "queue_length"
                ],

            "average_wait":
                queue_data[
                    "average_wait"
                ],

            "longest_wait":
                queue_data[
                    "longest_wait"
                ],

            "alert":
                queue_data[
                    "alert"
                ]
        }


        with self.snapshot_lock:

            self.latest_snapshot = (
                snapshot
            )


    # ==================================================
    # DRAW DEVELOPMENT WINDOW
    # ==================================================

    def draw_frame(
        self,
        frame,
        people,
        queue_data
    ):

        # ----------------------------------------------
        # QUEUE ZONE
        # ----------------------------------------------

        qx1, qy1, qx2, qy2 = (
            QUEUE_ZONE
        )


        cv2.rectangle(
            frame,
            (qx1, qy1),
            (qx2, qy2),
            (255, 0, 255),
            2
        )


        cv2.putText(
            frame,
            "BILLING QUEUE ZONE",
            (
                qx1 + 5,
                qy1 + 25
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 0, 255),
            2
        )


        # ----------------------------------------------
        # TRACKED PEOPLE
        # ----------------------------------------------

        for person in people:

            track_id = person[
                "track_id"
            ]

            x1, y1, x2, y2 = (
                person[
                    "bbox"
                ]
            )

            foot_x, foot_y = (
                person[
                    "foot"
                ]
            )


            # Bounding box

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )


            # Foot point

            cv2.circle(
                frame,
                (
                    foot_x,
                    foot_y
                ),
                5,
                (0, 0, 255),
                -1
            )


            label = (
                f"ID {track_id}"
            )


            # If person is currently
            # inside queue zone

            wait_time = (
                queue_data[
                    "wait_by_track"
                ].get(
                    track_id
                )
            )


            if wait_time is not None:

                label += (
                    f" | WAIT "
                    f"{wait_time:.1f}s"
                )


            cv2.putText(
                frame,
                label,
                (
                    x1,
                    max(
                        y1 - 10,
                        20
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2
            )


        # ----------------------------------------------
        # INFORMATION PANEL
        # ----------------------------------------------

        cv2.rectangle(
            frame,
            (10, 10),
            (390, 125),
            (0, 0, 0),
            -1
        )


        cv2.putText(
            frame,
            (
                f"Queue Length: "
                f"{queue_data['queue_length']}"
            ),
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            (
                f"Average Wait: "
                f"{queue_data['average_wait']:.1f}s"
            ),
            (20, 72),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            (
                f"Longest Wait: "
                f"{queue_data['longest_wait']:.1f}s"
            ),
            (20, 104),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


        # ----------------------------------------------
        # QUEUE ALERT
        # ----------------------------------------------

        if queue_data[
            "alert"
        ]:

            cv2.rectangle(
                frame,
                (10, 140),
                (
                    FRAME_WIDTH - 10,
                    195
                ),
                (0, 0, 255),
                -1
            )


            cv2.putText(
                frame,
                (
                    "QUEUE ALERT - "
                    "OPEN ANOTHER COUNTER"
                ),
                (25, 175),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )


        return frame


    # ==================================================
    # MAIN AI LOOP
    # ==================================================

    def run(
        self,
        display=True
    ):

        print()
        print(
            "Queue engine started."
        )

        self.running = True

        self.last_error = None


        try:

            while self.running:

                # --------------------------------------
                # READ CAMERA FRAME
                # --------------------------------------

                frame = (
                    self.camera.read()
                )


                if frame is None:

                    raise RuntimeError(
                        "Camera frame unavailable."
                    )


                # --------------------------------------
                # TIME FOR WAIT CALCULATION
                # --------------------------------------

                now = time.monotonic()


                # --------------------------------------
                # YOLO + BYTETRACK
                # --------------------------------------

                people = (
                    self.tracker.track(
                        frame
                    )
                )


                # --------------------------------------
                # QUEUE ANALYSIS
                # --------------------------------------

                queue_data = (
                    self.queue_analyzer.update(
                        people,
                        now
                    )
                )


                # --------------------------------------
                # UPDATE API STATE
                # --------------------------------------

                self.update_snapshot(
                    people,
                    queue_data
                )


                # --------------------------------------
                # OPTIONAL OPENCV WINDOW
                # --------------------------------------

                if display:

                    display_frame = (
                        self.draw_frame(
                            frame,
                            people,
                            queue_data
                        )
                    )


                    cv2.imshow(
                        (
                            "RetailEdge AI "
                            "- Queue Monitor"
                        ),
                        display_frame
                    )


                    key = (
                        cv2.waitKey(1)
                        & 0xFF
                    )


                    if key == ord("q"):

                        self.running = False


        except Exception as error:

            self.last_error = str(
                error
            )

            print(
                "Queue engine error:",
                self.last_error
            )


        finally:

            self.running = False

            self.camera.release()


            if display:

                cv2.destroyAllWindows()


            print(
                "Queue engine stopped."
            )