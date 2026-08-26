from pydantic import BaseModel


class QueueResponse(
    BaseModel
):

    timestamp: float

    tracked_people: int

    queue_length: int

    average_wait: float

    longest_wait: float

    alert: bool