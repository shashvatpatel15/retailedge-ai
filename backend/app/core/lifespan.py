from contextlib import (
    asynccontextmanager
)

from fastapi import FastAPI


from app.services.edge_service import (
    start_edge_engine,
    stop_edge_engine
)

from app.services.cloud_sync_service import (
    start_cloud_sync,
    stop_cloud_sync
)


@asynccontextmanager
async def lifespan(
    app: FastAPI
):

    # ============================================
    # STARTUP
    # ============================================

    print(
        "Starting RetailEdge backend..."
    )


    # Start local AI first.

    start_edge_engine()


    # Then start cloud synchronization.

    start_cloud_sync()


    yield


    # ============================================
    # SHUTDOWN
    # ============================================

    print(
        "Shutting down RetailEdge backend..."
    )


    # Stop uploading first.

    stop_cloud_sync()


    # Then stop camera / AI.

    stop_edge_engine()