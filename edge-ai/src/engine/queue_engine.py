import cv2
import time
import threading
from copy import deepcopy

from core.camera import CameraStream
from core.config import (
    FRAME_WIDTH,
    QUEUE_ZONE,
    DETECTOR_BACKEND,
    FRAME_SKIP
)
from analytics.queue_analyzer import QueueAnalyzer


class QueueEngine:

    def __init__(self, backend=None, camera_source=None):
        print("================================")
        print("RetailEdge AI")
        print("Smart Queue Monitoring Engine")
        print("================================")

        self.backend = backend or DETECTOR_BACKEND
        print(f"Target Vision Backend: {self.backend.upper()}")

        # Camera
        self.camera = CameraStream(source=camera_source)


        # Initialize Vision Pipeline
        self.detector = None
        self.tracker = None
        self._init_vision_pipeline()

        # Queue business logic
        self.queue_analyzer = QueueAnalyzer()

        # Thread-safe shared queue state
        self.snapshot_lock = threading.Lock()

        self.latest_snapshot = {
            "timestamp": time.time(),
            "backend": self.backend,
            "tracked_people": 0,
            "queue_length": 0,
            "average_wait": 0.0,
            "longest_wait": 0.0,
            "alert": False,
            "fps": 0.0,
            "inference_time_ms": 0.0
        }

        self.running = False
        self.last_error = None
        self.current_fps = 0.0
        self.last_inference_ms = 0.0

    def _init_vision_pipeline(self):
        """
        Initialize lightweight NCNN + pure Python tracker for Raspberry Pi,
        or fallback to Ultralytics YOLO tracker.
        """
        if self.backend == "ncnn":
            try:
                from detection.ncnn_person_detector import NcnnPersonDetector
                from tracking.lightweight_tracker import LightweightTracker

                print("Initializing ultra-lightweight NCNN + IoU tracker...")
                self.detector = NcnnPersonDetector()
                self.tracker = LightweightTracker(max_age=15, min_hits=1)
                self.backend = "ncnn"
                print("Lightweight NCNN Edge Pipeline ready.")
                return
            except Exception as e:
                print(f"NCNN initialization failed ({e}). Checking fallback...")

        # Fallback to YOLO ByteTrack if available
        try:
            from tracking.yolo_bytetrack import PersonTracker
            print("Initializing YOLO + ByteTrack...")
            self.tracker = PersonTracker()
            self.detector = None
            self.backend = "yolo"
            print("YOLO ByteTrack Pipeline ready.")
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize vision pipeline with backend '{self.backend}'. "
                f"Error: {e}. Ensure NCNN model or YOLO weights are installed."
            )

    # ==================================================
    # GET CURRENT QUEUE STATE
    # ==================================================

    def get_snapshot(self):
        with self.snapshot_lock:
            return deepcopy(self.latest_snapshot)

    # ==================================================
    # STOP ENGINE
    # ==================================================

    def stop(self):
        self.running = False

    # ==================================================
    # UPDATE SHARED STATE
    # ==================================================

    def update_snapshot(self, people, queue_data, fps=0.0, inference_ms=0.0):
        snapshot = {
            "timestamp": time.time(),
            "backend": self.backend,
            "tracked_people": len(people),
            "queue_length": queue_data["queue_length"],
            "average_wait": round(queue_data["average_wait"], 1),
            "longest_wait": round(queue_data["longest_wait"], 1),
            "alert": queue_data["alert"],
            "fps": round(fps, 1),
            "inference_time_ms": round(inference_ms, 1)
        }

        with self.snapshot_lock:
            self.latest_snapshot = snapshot

    # ==================================================
    # DRAW DEVELOPMENT WINDOW
    # ==================================================

    def draw_frame(self, frame, people, queue_data, fps=0.0):
        # ----------------------------------------------
        # QUEUE ZONE
        # ----------------------------------------------
        qx1, qy1, qx2, qy2 = QUEUE_ZONE

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
            (qx1 + 5, qy1 + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 0, 255),
            2
        )

        # ----------------------------------------------
        # TRACKED PEOPLE
        # ----------------------------------------------
        for person in people:
            track_id = person["track_id"]
            x1, y1, x2, y2 = person["bbox"]
            foot_x, foot_y = person["foot"]

            # Bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Foot point
            cv2.circle(frame, (foot_x, foot_y), 5, (0, 0, 255), -1)

            label = f"ID {track_id}"
            wait_time = queue_data["wait_by_track"].get(track_id)

            if wait_time is not None:
                label += f" | WAIT {wait_time:.1f}s"

            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2
            )

        # ----------------------------------------------
        # INFORMATION PANEL
        # ----------------------------------------------
        cv2.rectangle(frame, (10, 10), (390, 140), (0, 0, 0), -1)

        cv2.putText(
            frame,
            f"Queue Length: {queue_data['queue_length']}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Average Wait: {queue_data['average_wait']:.1f}s",
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Longest Wait: {queue_data['longest_wait']:.1f}s",
            (20, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"FPS: {fps:.1f} | Backend: {self.backend.upper()}",
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            1
        )

        # ----------------------------------------------
        # QUEUE ALERT
        # ----------------------------------------------
        if queue_data["alert"]:
            cv2.rectangle(
                frame,
                (10, 150),
                (FRAME_WIDTH - 10, 200),
                (0, 0, 255),
                -1
            )

            cv2.putText(
                frame,
                "QUEUE ALERT - OPEN ANOTHER COUNTER",
                (25, 185),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

        return frame

    # ==================================================
    # MAIN AI LOOP
    # ==================================================

    def run(self, display=False):
        print()
        print(f"RetailEdge Queue Engine started (Headless={not display}, Backend={self.backend}).")

        self.running = True
        self.last_error = None
        frame_count = 0
        fps_start_time = time.perf_counter()

        try:
            while self.running:
                loop_start = time.perf_counter()

                # Read Camera Frame
                frame = self.camera.read()

                if frame is None:
                    raise RuntimeError("Camera frame unavailable.")

                now = time.monotonic()
                inference_ms = 0.0

                # Frame skipping logic if configured
                if FRAME_SKIP > 0 and (frame_count % (FRAME_SKIP + 1) != 0):
                    frame_count += 1
                    time.sleep(0.01)
                    continue

                # --------------------------------------
                # DETECTION & TRACKING
                # --------------------------------------
                if self.detector is not None:
                    # NCNN lightweight detection + Pure Python Tracker
                    detections, inf_time = self.detector.detect(frame)
                    people = self.tracker.update(detections)
                    inference_ms = inf_time * 1000.0
                else:
                    # YOLO ByteTrack tracking
                    t0 = time.perf_counter()
                    people = self.tracker.track(frame)
                    inference_ms = (time.perf_counter() - t0) * 1000.0

                # --------------------------------------
                # QUEUE ANALYSIS
                # --------------------------------------
                queue_data = self.queue_analyzer.update(people, now)

                # FPS Calculation
                frame_count += 1
                loop_duration = time.perf_counter() - loop_start
                instant_fps = 1.0 / max(loop_duration, 0.001)

                if frame_count % 10 == 0:
                    elapsed = time.perf_counter() - fps_start_time
                    self.current_fps = 10.0 / max(elapsed, 0.001)
                    fps_start_time = time.perf_counter()
                else:
                    self.current_fps = instant_fps

                self.last_inference_ms = inference_ms

                # --------------------------------------
                # UPDATE SNAPSHOT
                # --------------------------------------
                self.update_snapshot(people, queue_data, self.current_fps, inference_ms)

                # --------------------------------------
                # OPTIONAL OPENCV WINDOW (NON-HEADLESS)
                # --------------------------------------
                if display:
                    display_frame = self.draw_frame(frame, people, queue_data, self.current_fps)
                    cv2.imshow("RetailEdge AI - Queue Monitor", display_frame)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        self.running = False

        except Exception as error:
            self.last_error = str(error)
            print("Queue engine error:", self.last_error)

        finally:
            self.running = False
            self.camera.release()

            if display:
                cv2.destroyAllWindows()

            print("Queue engine stopped.")