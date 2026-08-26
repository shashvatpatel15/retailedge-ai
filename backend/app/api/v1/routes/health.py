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


router = APIRouter()


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