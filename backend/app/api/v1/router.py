from fastapi import APIRouter, Depends

from app.api.v1.routes import (
    health,
    queue
)
from app.core.security import verify_edge_api_key


router = APIRouter(dependencies=[Depends(verify_edge_api_key)])



# -----------------------------------------
# HEALTH
# -----------------------------------------

router.include_router(

    health.router,

    prefix="/health",

    tags=["Health"]
)


# -----------------------------------------
# QUEUE
# -----------------------------------------

router.include_router(

    queue.router,

    prefix="/queue",

    tags=["Queue"]
)