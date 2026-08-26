from engine.queue_engine import QueueEngine


def main():

    engine = QueueEngine()

    engine.run(
        display=True
    )


if __name__ == "__main__":

    main()