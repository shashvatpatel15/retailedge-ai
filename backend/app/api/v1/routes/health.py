from fastapi import APIRouter
from app.schemas.health import HealthResponse
from app.services.edge_service import get_engine_health


router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse
)
def get_health():
    health = get_engine_health()
    is_running = bool(health.get("running", False))

    return {
        "status": "ok" if is_running else "degraded",
        "edge_engine_running": is_running,
        "error": health.get("error")
    }