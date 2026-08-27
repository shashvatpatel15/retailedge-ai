from pathlib import Path
import time

import cv2
import numpy as np
import ncnn

from core.config import (
    PROJECT_ROOT,
    YOLO_MODEL,
    YOLO_IMAGE_SIZE,
    PERSON_CONFIDENCE,
    NCNN_NUM_THREADS,
)


PERSON_CLASS_ID = 0
NMS_THRESHOLD = 0.45


class NcnnPersonDetector:

    def __init__(self, model_path=None):
        target = Path(model_path) if model_path else Path(YOLO_MODEL)

        # Resolve model directory path
        candidate_dirs = [
            target,
            PROJECT_ROOT / target,
            PROJECT_ROOT / "yolo11n_ncnn_model",
            Path.cwd() / target,
            Path.cwd() / "yolo11n_ncnn_model"
        ]

        self.model_dir = None
        for candidate in candidate_dirs:
            if candidate.exists() and candidate.is_dir():
                param = candidate / "model.ncnn.param"
                bin_file = candidate / "model.ncnn.bin"
                if param.exists() and bin_file.exists():
                    self.model_dir = candidate
                    break

        if self.model_dir is None:
            raise FileNotFoundError(
                f"NCNN model directory containing model.ncnn.param and model.ncnn.bin "
                f"not found. Searched in: {[str(c) for c in candidate_dirs]}"
            )

        self.param_file = self.model_dir / "model.ncnn.param"
        self.bin_file = self.model_dir / "model.ncnn.bin"

        print(f"Loading lightweight NCNN detector from: {self.model_dir}")
        print(f"Allocating {NCNN_NUM_THREADS} CPU threads for ARM inference...")

        self.net = ncnn.Net()
        self.net.opt.num_threads = NCNN_NUM_THREADS
        self.net.opt.use_vulkan_compute = False

        param_result = self.net.load_param(str(self.param_file))
        model_result = self.net.load_model(str(self.bin_file))

        if param_result != 0:
            raise RuntimeError(f"Could not load NCNN param file: {self.param_file}")

        if model_result != 0:
            raise RuntimeError(f"Could not load NCNN model file: {self.bin_file}")

        print("NCNN detector ready.")

    # ==================================================
    # PREPROCESS
    # ==================================================

    def preprocess(self, frame):
        original_height, original_width = frame.shape[:2]

        scale = min(
            YOLO_IMAGE_SIZE / original_width,
            YOLO_IMAGE_SIZE / original_height
        )

        resized_width = int(round(original_width * scale))
        resized_height = int(round(original_height * scale))

        resized = cv2.resize(frame, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)

        # YOLO-style letterbox background
        canvas = np.full(
            (YOLO_IMAGE_SIZE, YOLO_IMAGE_SIZE, 3),
            114,
            dtype=np.uint8
        )

        pad_x = (YOLO_IMAGE_SIZE - resized_width) // 2
        pad_y = (YOLO_IMAGE_SIZE - resized_height) // 2

        canvas[
            pad_y:pad_y + resized_height,
            pad_x:pad_x + resized_width
        ] = resized

        rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        tensor = rgb.astype(np.float32) / 255.0

        # HWC -> CHW
        tensor = np.transpose(tensor, (2, 0, 1))
        tensor = np.ascontiguousarray(tensor)

        return tensor, scale, pad_x, pad_y

    # ==================================================
    # DECODE YOLO OUTPUT
    # ==================================================

    def decode(self, output, original_width, original_height, scale, pad_x, pad_y):
        output = np.array(output)

        # YOLO11 NCNN output is (84, 2100) -> transpose to (2100, 84)
        if output.ndim == 2 and output.shape[0] == 84:
            output = output.T

        boxes = []
        scores = []

        for detection in output:
            confidence = float(detection[4 + PERSON_CLASS_ID])

            if confidence < PERSON_CONFIDENCE:
                continue

            center_x = float(detection[0])
            center_y = float(detection[1])
            width = float(detection[2])
            height = float(detection[3])

            # Convert from letterboxed coordinates back to original frame
            x1 = (center_x - width / 2 - pad_x) / scale
            y1 = (center_y - height / 2 - pad_y) / scale
            x2 = (center_x + width / 2 - pad_x) / scale
            y2 = (center_y + height / 2 - pad_y) / scale

            x1 = max(0, min(original_width - 1, int(x1)))
            y1 = max(0, min(original_height - 1, int(y1)))
            x2 = max(0, min(original_width - 1, int(x2)))
            y2 = max(0, min(original_height - 1, int(y2)))

            box_width = x2 - x1
            box_height = y2 - y1

            if box_width <= 0 or box_height <= 0:
                continue

            boxes.append([x1, y1, box_width, box_height])
            scores.append(confidence)

        if not boxes:
            return []

        indices = cv2.dnn.NMSBoxes(
            boxes,
            scores,
            PERSON_CONFIDENCE,
            NMS_THRESHOLD
        )

        people = []
        for index in indices:
            index = int(np.array(index).flatten()[0])
            x, y, width, height = boxes[index]
            x2 = x + width
            y2 = y + height

            foot_x = (x + x2) // 2
            foot_y = y2

            people.append({
                "bbox": (x, y, x2, y2),
                "foot": (foot_x, foot_y),
                "confidence": float(scores[index])
            })

        return people

    # ==================================================
    # DETECT PEOPLE
    # ==================================================

    def detect(self, frame):
        original_height, original_width = frame.shape[:2]
        tensor, scale, pad_x, pad_y = self.preprocess(frame)

        start_time = time.perf_counter()

        with self.net.create_extractor() as ex:
            input_mat = ncnn.Mat(tensor).clone()
            input_result = ex.input("in0", input_mat)

            if input_result != 0:
                raise RuntimeError("Could not send image to NCNN model.")

            extract_result, output = ex.extract("out0")

            if extract_result != 0:
                raise RuntimeError("Could not extract NCNN model output.")

        inference_time = time.perf_counter() - start_time
        people = self.decode(output, original_width, original_height, scale, pad_x, pad_y)

        return people, inference_time