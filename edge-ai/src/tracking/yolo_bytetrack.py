from ultralytics import YOLO

from core.config import (
    YOLO_MODEL,
    PERSON_CLASS_ID,
    PERSON_CONFIDENCE,
    YOLO_IMAGE_SIZE
)


class PersonTracker:

    def __init__(self):

        print(
            f"Loading YOLO model: "
            f"{YOLO_MODEL}"
        )

        self.model = YOLO(
            YOLO_MODEL
        )

        print(
            "YOLO loaded."
        )


    def track(
        self,
        frame
    ):

        results = self.model.track(

            frame,

            persist=True,

            tracker="bytetrack.yaml",

            classes=[
                PERSON_CLASS_ID
            ],

            conf=
                PERSON_CONFIDENCE,

            imgsz=
                YOLO_IMAGE_SIZE,

            verbose=False
        )


        boxes = (
            results[0].boxes
        )


        if boxes.id is None:

            return []


        ids = (
            boxes.id
            .int()
            .cpu()
            .tolist()
        )


        coordinates = (
            boxes.xyxy
            .cpu()
            .tolist()
        )


        confidences = (
            boxes.conf
            .cpu()
            .tolist()
        )


        people = []


        for (
            track_id,
            box,
            confidence
        ) in zip(
            ids,
            coordinates,
            confidences
        ):

            x1, y1, x2, y2 = (
                map(
                    int,
                    box
                )
            )


            foot_x = (
                x1 + x2
            ) // 2


            foot_y = y2


            people.append(
                {
                    "track_id":
                        track_id,

                    "bbox":
                        (
                            x1,
                            y1,
                            x2,
                            y2
                        ),

                    "foot":
                        (
                            foot_x,
                            foot_y
                        ),

                    "confidence":
                        float(
                            confidence
                        )
                }
            )


        return people