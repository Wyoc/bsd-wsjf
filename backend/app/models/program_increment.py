from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class ProgramIncrementBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="PI name (e.g., PI18)")
    description: str = Field("", max_length=500, description="PI description")
    start_date: datetime = Field(..., description="PI start date")
    end_date: datetime = Field(..., description="PI end date")
    status: str = Field(
        "Planning", 
        description="PI status (Planning, Active, Completed, Cancelled)"
    )

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: datetime, info) -> datetime:
        """Validate that end date is after start date."""
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError("End date must be after start date")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate PI status."""
        allowed_statuses = ["Planning", "Active", "Completed", "Cancelled"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of {allowed_statuses}")
        return v


class ProgramIncrementCreate(ProgramIncrementBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "PI18",
                "description": "Q4 2025 Product Enhancement Initiative",
                "start_date": "2025-10-01T00:00:00Z",
                "end_date": "2025-12-20T23:59:59Z",
                "status": "Planning"
            }
        }
    }


class ProgramIncrementUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """Validate PI status."""
        if v is not None:
            allowed_statuses = ["Planning", "Active", "Completed", "Cancelled"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of {allowed_statuses}")
        return v


class ProgramIncrement(ProgramIncrementBase):
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    created_date: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    item_count: int = Field(0, description="Number of WSJF items in this PI")

    class Config:
        from_attributes = True


class ProgramIncrementResponse(ProgramIncrement):
    pass


class ProgramIncrementStats(BaseModel):
    pi_id: UUID
    pi_name: str
    total_items: int
    avg_wsjf_score: float
    status_distribution: dict[str, int]
    team_distribution: dict[str, int]