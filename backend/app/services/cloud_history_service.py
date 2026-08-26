import requests

from app.core.config import (
    SUPABASE_HISTORY_URL,
    EDGE_DEVICE_ID
)


def get_cloud_history(
    device_id=None
):

    if not SUPABASE_HISTORY_URL:

        raise RuntimeError(
            "SUPABASE_HISTORY_URL missing"
        )


    selected_device = (
        device_id
        or EDGE_DEVICE_ID
    )


    response = requests.get(
        SUPABASE_HISTORY_URL,
        params={
            "device_id":
                selected_device
        },
        timeout=5
    )


    response.raise_for_status()


    return response.json()