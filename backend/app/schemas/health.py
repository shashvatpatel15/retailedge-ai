from typing import Optional

from pydantic import BaseModel


class HealthResponse(
    BaseModel
):

    status: str

    edge_engine_running: bool

    error: Optional[str] = None