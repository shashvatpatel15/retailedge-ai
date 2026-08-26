from engine.queue_engine import QueueEngine


def main():

    engine = QueueEngine()

    # Raspberry Pi OS Lite is headless.
    # Do not open an OpenCV GUI window.
    engine.run(
        display=False
    )


if __name__ == "__main__":

    main()