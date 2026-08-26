from ultralytics import YOLO


MODEL_PATH = "yolo11n.pt"


def main():

    print(
        "Loading YOLO11n..."
    )


    model = YOLO(
        MODEL_PATH
    )


    print(
        "Exporting to NCNN..."
    )


    model.export(
        format="ncnn",
        imgsz=320
    )


    print(
        "NCNN export complete."
    )


if __name__ == "__main__":

    main()