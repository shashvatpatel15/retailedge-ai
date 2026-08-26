from fastapi import (
    APIRouter,
    HTTPException
)

from app.schemas.queue import (
    QueueResponse
)

from app.services.edge_service import (
    get_queue_snapshot
)

from app.services.cloud_history_service import (
    get_cloud_history
)


router = APIRouter()


# ============================================
# LIVE QUEUE DATA
# ============================================

@router.get(
    "",
    response_model=QueueResponse
)
def get_queue():

    data = get_queue_snapshot()


    if data is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Queue AI engine "
                "is not available."
            )
        )


    return data


# ============================================
# CLOUD QUEUE HISTORY
# ============================================

@router.get(
    "/history"
)
def get_queue_history():

    try:

        return get_cloud_history()

    except Exception as error:

        raise HTTPException(
            status_code=503,
            detail=(
                "Cloud history unavailable: "
                + str(error)
            )
        )