import sys
import threading
from pathlib import Path


from app.state.app_state import (
    app_state
)


# ==================================================
# LOCATE EDGE-AI SOURCE DIRECTORY
# ==================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)


EDGE_AI_SRC = (
    PROJECT_ROOT
    /
    "edge-ai"
    /
    "src"
)


if str(EDGE_AI_SRC) not in sys.path:

    sys.path.insert(
        0,
        str(EDGE_AI_SRC)
    )


# Now Python can import:
#
# edge-ai/src/engine/queue_engine.py

from engine.queue_engine import QueueEngine


# ==================================================
# START EDGE AI
# ==================================================

def start_edge_engine():

    # Already running

    if (
        app_state.engine
        is not None

        and

        app_state.engine.running
    ):

        return


    print(
        "Starting RetailEdge Queue AI..."
    )


    try:

        # Create QueueEngine

        app_state.engine = (
            QueueEngine()
        )


        # Run AI loop separately
        # so FastAPI remains responsive

        app_state.engine_thread = (
            threading.Thread(

                target=
                    app_state.engine.run,

                kwargs={
                    "display": False
                },

                daemon=True,

                name=
                    "retailedge-queue-engine"
            )
        )


        app_state.engine_thread.start()


        app_state.startup_error = None


        print(
            "RetailEdge Queue AI started."
        )


    except Exception as error:

        app_state.startup_error = str(
            error
        )

        app_state.engine = None

        app_state.engine_thread = None


        print(
            "Could not start Queue AI:",
            app_state.startup_error
        )


# ==================================================
# STOP EDGE AI
# ==================================================

def stop_edge_engine():

    print(
        "Stopping RetailEdge Queue AI..."
    )


    if app_state.engine is not None:

        app_state.engine.stop()


    if (
        app_state.engine_thread
        is not None

        and

        app_state.engine_thread.is_alive()
    ):

        app_state.engine_thread.join(
            timeout=3
        )


    print(
        "RetailEdge Queue AI stopped."
    )


# ==================================================
# GET CURRENT QUEUE DATA
# ==================================================

def get_queue_snapshot():

    if app_state.engine is None:

        return None


    return (
        app_state.engine.get_snapshot()
    )


# ==================================================
# ENGINE STATUS
# ==================================================

def get_engine_health():

    engine = app_state.engine


    if engine is None:

        return {

            "running":
                False,

            "error":
                app_state.startup_error
        }


    error = (

        app_state.startup_error

        or

        engine.last_error
    )


    return {

        "running":
            engine.running,

        "error":
            error
    }