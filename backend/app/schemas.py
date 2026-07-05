from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    """
    Data the user must send when creating a ticket.
    """

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    message: str = Field(
        min_length=1,
    )

    category: str | None = Field(
        default=None,
        max_length=100,
    )


class TicketResponse(BaseModel):
    """
    Data returned by the API after reading or creating a ticket.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    message: str
    category: str | None
    sentiment: str
    confidence: float
    created_at: datetime