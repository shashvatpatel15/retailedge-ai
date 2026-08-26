import threading
import uuid

from datetime import (
    datetime,
    timezone
)

import requests


from app.core.config import (
    SUPABASE_INGEST_URL,
    EDGE_INGEST_TOKEN,
    EDGE_DEVICE_ID,
    CLOUD_SYNC_ENABLED,
    CLOUD_SYNC_INTERVAL_SECONDS,
    CLOUD_SYNC_BATCH_SIZE
)

from app.services.edge_service import (
    get_queue_snapshot
)

from app.services.local_db_service import (
    init_local_db,
    save_pending_metric,
    get_pending_metrics,
    delete_pending_metric,
    get_pending_count
)

from app.state.app_state import (
    app_state
)


# ============================================
# CREATE CLOUD PAYLOAD
# ============================================

def build_payload(
    snapshot
):

    timestamp = snapshot.get(
        "timestamp",
        datetime.now(
            timezone.utc
        ).timestamp()
    )


    recorded_at = (
        datetime
        .fromtimestamp(
            timestamp,
            tz=timezone.utc
        )
        .isoformat()
    )


    return {

        "event_id":
            str(
                uuid.uuid4()
            ),

        "device_id":
            EDGE_DEVICE_ID,

        "recorded_at":
            recorded_at,

        "tracked_people":
            int(
                snapshot.get(
                    "tracked_people",
                    0
                )
            ),

        "queue_length":
            int(
                snapshot.get(
                    "queue_length",
                    0
                )
            ),

        "average_wait":
            float(
                snapshot.get(
                    "average_wait",
                    0.0
                )
            ),

        "longest_wait":
            float(
                snapshot.get(
                    "longest_wait",
                    0.0
                )
            ),

        "alert":
            bool(
                snapshot.get(
                    "alert",
                    False
                )
            )
    }


# ============================================
# SEND ONE CLOUD RECORD
# ============================================

def send_payload(
    payload
):

    headers = {

        "x-edge-token":
            EDGE_INGEST_TOKEN,

        "Content-Type":
            "application/json"
    }


    response = requests.post(

        SUPABASE_INGEST_URL,

        headers=headers,

        json=payload,

        timeout=5
    )


    response.raise_for_status()


    return response.json()


# ============================================
# CAPTURE CURRENT QUEUE STATE
# ============================================

def capture_queue_snapshot():

    snapshot = (
        get_queue_snapshot()
    )


    if snapshot is None:

        return


    payload = (
        build_payload(
            snapshot
        )
    )


    # IMPORTANT:
    #
    # Save locally BEFORE trying cloud.

    save_pending_metric(
        payload
    )


    print(
        "Local queue metric stored:",
        f"queue="
        f"{payload['queue_length']}"
    )


# ============================================
# SYNC STORED RECORDS
# ============================================

def sync_pending_metrics():

    pending_metrics = (
        get_pending_metrics(
            CLOUD_SYNC_BATCH_SIZE
        )
    )


    if not pending_metrics:

        return


    for payload in pending_metrics:

        try:

            send_payload(
                payload
            )


            # Cloud confirmed success.
            #
            # Only now remove local copy.

            delete_pending_metric(
                payload[
                    "event_id"
                ]
            )


            app_state.last_cloud_sync_at = (
                datetime.now(
                    timezone.utc
                ).isoformat()
            )


            app_state.last_cloud_sync_error = (
                None
            )


            print(
                "Cloud sync success:",
                f"queue="
                f"{payload['queue_length']}, "
                f"alert="
                f"{payload['alert']}"
            )


        except Exception as error:

            app_state.last_cloud_sync_error = (
                str(error)
            )


            print(
                "Cloud sync failed:",
                error
            )


            # Stop this batch.
            #
            # If cloud is unavailable,
            # repeatedly trying every remaining
            # row is unnecessary.

            break


# ============================================
# CLOUD SYNC LOOP
# ============================================

def cloud_sync_loop():

    print(
        "Cloud sync worker started."
    )


    app_state.cloud_sync_running = True


    try:

        while not (
            app_state
            .cloud_sync_stop_event
            .wait(
                CLOUD_SYNC_INTERVAL_SECONDS
            )
        ):

            try:

                # ====================================
                # STEP 1
                # CAPTURE NEW QUEUE METRIC LOCALLY
                # ====================================

                capture_queue_snapshot()


                # ====================================
                # STEP 2
                # TRY SYNCING ALL PENDING RECORDS
                # ====================================

                if CLOUD_SYNC_ENABLED:

                    sync_pending_metrics()


                pending_count = (
                    get_pending_count()
                )


                print(
                    "Pending cloud records:",
                    pending_count
                )


            except Exception as error:

                app_state.last_cloud_sync_error = (
                    str(error)
                )


                print(
                    "Cloud worker error:",
                    error
                )


    finally:

        app_state.cloud_sync_running = False


        print(
            "Cloud sync worker stopped."
        )


# ============================================
# START CLOUD SYNC
# ============================================

def start_cloud_sync():

    # SQLite should work even when cloud
    # connectivity does not.

    init_local_db()


    if (
        app_state.cloud_sync_thread
        is not None

        and

        app_state
        .cloud_sync_thread
        .is_alive()
    ):

        return


    if CLOUD_SYNC_ENABLED:

        if not SUPABASE_INGEST_URL:

            print(
                "SUPABASE_INGEST_URL missing."
            )


        if not EDGE_INGEST_TOKEN:

            print(
                "EDGE_INGEST_TOKEN missing."
            )


    print(
        "Starting local/cloud sync worker..."
    )


    app_state.cloud_sync_stop_event = (
        threading.Event()
    )


    app_state.cloud_sync_thread = (
        threading.Thread(

            target=
                cloud_sync_loop,

            daemon=True,

            name=
                "retailedge-cloud-sync"
        )
    )


    app_state.cloud_sync_thread.start()


# ============================================
# STOP CLOUD SYNC
# ============================================

def stop_cloud_sync():

    if (
        app_state.cloud_sync_stop_event
        is not None
    ):

        app_state.cloud_sync_stop_event.set()


    if (
        app_state.cloud_sync_thread
        is not None

        and

        app_state
        .cloud_sync_thread
        .is_alive()
    ):

        app_state.cloud_sync_thread.join(
            timeout=5
        )


    app_state.cloud_sync_running = False