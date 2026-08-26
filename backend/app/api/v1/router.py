from fastapi import APIRouter

from app.api.v1.routes import (
    health,
    queue
)


router = APIRouter()


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