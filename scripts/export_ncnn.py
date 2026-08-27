from pathlib import Path

from ultralytics import YOLO


# ==================================================
# PATHS
# ==================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


MODEL_PATH = (
    PROJECT_ROOT
    / "yolo11n.pt"
)


# ==================================================
# EXPORT SETTINGS
# ==================================================

IMAGE_SIZE = 320


# ==================================================
# EXPORT YOLO11N -> NCNN
# ==================================================

def main():

    print()
    print(
        "================================"
    )

    print(
        "RetailEdge AI - NCNN Export"
    )

    print(
        "================================"
    )

    print(
        f"Model: {MODEL_PATH}"
    )

    print(
        f"Image size: {IMAGE_SIZE}"
    )

    print()


    # ----------------------------------------------
    # CHECK MODEL
    # ----------------------------------------------

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"YOLO model not found: "
            f"{MODEL_PATH}"
        )


    # ----------------------------------------------
    # LOAD YOLO
    # ----------------------------------------------

    print(
        "Loading YOLO11n..."
    )


    model = YOLO(
        str(
            MODEL_PATH
        )
    )


    print(
        "YOLO11n loaded."
    )


    # ----------------------------------------------
    # EXPORT TO NCNN
    # ----------------------------------------------

    print()
    print(
        "Exporting YOLO11n "
        "to NCNN..."
    )


    export_path = model.export(
        format="ncnn",
        imgsz=IMAGE_SIZE
    )


    # ----------------------------------------------
    # RESULT
    # ----------------------------------------------

    print()
    print(
        "================================"
    )

    print(
        "NCNN EXPORT COMPLETE"
    )

    print(
        "================================"
    )

    print(
        f"Exported model: "
        f"{export_path}"
    )

    print()
    print(
        "This model is intended "
        "for Raspberry Pi 3 B+."
    )

    print(
        "Inference size: 320x320"
    )

    print()


if __name__ == "__main__":

    main()