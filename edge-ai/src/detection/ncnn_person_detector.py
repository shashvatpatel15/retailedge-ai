from pathlib import Path
import time

import cv2
import numpy as np
import ncnn

from core.config import (
    YOLO_MODEL,
    YOLO_IMAGE_SIZE,
    PERSON_CONFIDENCE,
)


PERSON_CLASS_ID = 0
NMS_THRESHOLD = 0.45


class NcnnPersonDetector:

    def __init__(self):

        self.model_dir = Path(
            YOLO_MODEL
        )

        self.param_file = (
            self.model_dir
            / "model.ncnn.param"
        )

        self.bin_file = (
            self.model_dir
            / "model.ncnn.bin"
        )


        if not self.param_file.exists():

            raise FileNotFoundError(
                f"NCNN param file not found: "
                f"{self.param_file}"
            )


        if not self.bin_file.exists():

            raise FileNotFoundError(
                f"NCNN model file not found: "
                f"{self.bin_file}"
            )


        print(
            "Loading lightweight NCNN detector..."
        )


        self.net = ncnn.Net()


        # Raspberry Pi 3 B+
        # Start with 2 threads.
        self.net.opt.num_threads = 2

        self.net.opt.use_vulkan_compute = False


        param_result = self.net.load_param(
            str(
                self.param_file
            )
        )


        model_result = self.net.load_model(
            str(
                self.bin_file
            )
        )


        if param_result != 0:

            raise RuntimeError(
                "Could not load NCNN param file."
            )


        if model_result != 0:

            raise RuntimeError(
                "Could not load NCNN model file."
            )


        print(
            "NCNN detector ready."
        )


    # ==================================================
    # PREPROCESS
    # ==================================================

    def preprocess(
        self,
        frame
    ):

        original_height, original_width = (
            frame.shape[:2]
        )


        scale = min(
            YOLO_IMAGE_SIZE
            / original_width,

            YOLO_IMAGE_SIZE
            / original_height
        )


        resized_width = int(
            round(
                original_width
                * scale
            )
        )


        resized_height = int(
            round(
                original_height
                * scale
            )
        )


        resized = cv2.resize(
            frame,
            (
                resized_width,
                resized_height
            )
        )


        # YOLO-style letterbox background.
        canvas = np.full(
            (
                YOLO_IMAGE_SIZE,
                YOLO_IMAGE_SIZE,
                3
            ),
            114,
            dtype=np.uint8
        )


        pad_x = (
            YOLO_IMAGE_SIZE
            - resized_width
        ) // 2


        pad_y = (
            YOLO_IMAGE_SIZE
            - resized_height
        ) // 2


        canvas[
            pad_y:
            pad_y + resized_height,

            pad_x:
            pad_x + resized_width
        ] = resized


        rgb = cv2.cvtColor(
            canvas,
            cv2.COLOR_BGR2RGB
        )


        tensor = (
            rgb.astype(
                np.float32
            )
            / 255.0
        )


        # HWC -> CHW
        tensor = np.transpose(
            tensor,
            (
                2,
                0,
                1
            )
        )


        tensor = np.ascontiguousarray(
            tensor
        )


        return (
            tensor,
            scale,
            pad_x,
            pad_y
        )


    # ==================================================
    # DECODE YOLO OUTPUT
    # ==================================================

    def decode(
        self,
        output,
        original_width,
        original_height,
        scale,
        pad_x,
        pad_y
    ):

        output = np.array(
            output
        )


        # YOLO11 NCNN output is normally:
        #
        # (84, 2100)
        #
        # Convert it to:
        #
        # (2100, 84)

        if (
            output.ndim == 2
            and
            output.shape[0] == 84
        ):

            output = output.T


        boxes = []

        scores = []


        for detection in output:

            # YOLO11:
            #
            # detection[0:4]
            # = x_center, y_center, width, height
            #
            # detection[4:]
            # = class scores
            #
            # COCO class 0 = person

            confidence = float(
                detection[
                    4 + PERSON_CLASS_ID
                ]
            )


            if (
                confidence
                <
                PERSON_CONFIDENCE
            ):

                continue


            center_x = float(
                detection[0]
            )

            center_y = float(
                detection[1]
            )

            width = float(
                detection[2]
            )

            height = float(
                detection[3]
            )


            # Convert from 320x320
            # letterboxed coordinates
            # back to original frame.

            x1 = (
                center_x
                - width / 2
                - pad_x
            ) / scale


            y1 = (
                center_y
                - height / 2
                - pad_y
            ) / scale


            x2 = (
                center_x
                + width / 2
                - pad_x
            ) / scale


            y2 = (
                center_y
                + height / 2
                - pad_y
            ) / scale


            x1 = max(
                0,
                min(
                    original_width - 1,
                    int(x1)
                )
            )


            y1 = max(
                0,
                min(
                    original_height - 1,
                    int(y1)
                )
            )


            x2 = max(
                0,
                min(
                    original_width - 1,
                    int(x2)
                )
            )


            y2 = max(
                0,
                min(
                    original_height - 1,
                    int(y2)
                )
            )


            box_width = (
                x2 - x1
            )

            box_height = (
                y2 - y1
            )


            if (
                box_width <= 0
                or
                box_height <= 0
            ):

                continue


            boxes.append(
                [
                    x1,
                    y1,
                    box_width,
                    box_height
                ]
            )


            scores.append(
                confidence
            )


        if not boxes:

            return []


        # Remove duplicate detections.
        indices = cv2.dnn.NMSBoxes(
            boxes,
            scores,
            PERSON_CONFIDENCE,
            NMS_THRESHOLD
        )


        people = []


        for index in indices:

            index = int(
                np.array(
                    index
                )
                .flatten()[0]
            )


            x, y, width, height = (
                boxes[index]
            )


            x2 = (
                x + width
            )

            y2 = (
                y + height
            )


            # Bottom-center point of person.
            #
            # Later QueueAnalyzer can use this
            # to determine whether the person
            # is inside the queue zone.

            foot_x = (
                x + x2
            ) // 2

            foot_y = y2


            people.append(
                {
                    "bbox": (
                        x,
                        y,
                        x2,
                        y2
                    ),

                    "foot": (
                        foot_x,
                        foot_y
                    ),

                    "confidence":
                        float(
                            scores[index]
                        )
                }
            )


        return people


    # ==================================================
    # DETECT PEOPLE
    # ==================================================

    def detect(
        self,
        frame
    ):

        original_height, original_width = (
            frame.shape[:2]
        )


        (
            tensor,
            scale,
            pad_x,
            pad_y
        ) = self.preprocess(
            frame
        )


        start_time = (
            time.perf_counter()
        )


        with self.net.create_extractor() as ex:

            input_mat = ncnn.Mat(
                tensor
            ).clone()


            input_result = ex.input(
                "in0",
                input_mat
            )


            if input_result != 0:

                raise RuntimeError(
                    "Could not send image "
                    "to NCNN model."
                )


            extract_result, output = (
                ex.extract(
                    "out0"
                )
            )


            if extract_result != 0:

                raise RuntimeError(
                    "Could not extract "
                    "NCNN model output."
                )


        inference_time = (
            time.perf_counter()
            -
            start_time
        )


        people = self.decode(
            output,
            original_width,
            original_height,
            scale,
            pad_x,
            pad_y
        )


        return (
            people,
            inference_time
        )