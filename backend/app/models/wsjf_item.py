from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field, field_validator

from .status import WSJFStatus

# Fibonacci values allowed for WSJF scoring
FIBONACCI_VALUES = [1, 2, 3, 5, 8, 13, 21]


class WSJFItemBase(BaseModel):
    subject: str = Field(
        ..., min_length=1, max_length=200, description="Feature/requirement name"
    )
    description: str = Field("", max_length=1000, description="Detailed explanation")
    business_value: int = Field(
        ..., description="Economic value delivered (Fibonacci: 1,2,3,5,8,13,21)"
    )
    time_criticality: int = Field(
        ..., description="Urgency and time sensitivity (Fibonacci: 1,2,3,5,8,13,21)"
    )
    risk_reduction: int = Field(
        ..., description="Risk mitigation value (Fibonacci: 1,2,3,5,8,13,21)"
    )
    job_size: int = Field(..., description="Effort required (Fibonacci: 1,2,3,5,8,13,21)")
    status: WSJFStatus = Field(WSJFStatus.NEW, description="Current state")
    owner: str | None = Field(None, max_length=100, description="Responsible person")
    team: str | None = Field(None, max_length=100, description="Assigned team")
    program_increment_id: UUID = Field(
        ..., description="Program Increment UUID reference"
    )

    @field_validator("business_value", "time_criticality", "risk_reduction", "job_size")
    @classmethod
    def validate_fibonacci_values(cls, v: int) -> int:
        """Validate that score values are valid Fibonacci numbers.

        Args:
            v (int): The score value to validate.

        Returns:
            int: The validated score value.

        Raises:
            ValueError: If score is not a valid Fibonacci value.
        """
        if v not in FIBONACCI_VALUES:
            raise ValueError(f"Score must be one of {FIBONACCI_VALUES}")
        return v


class WSJFItemCreate(WSJFItemBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "subject": "User Authentication System",
                "description": "Implement secure login and registration with OAuth2",
                "business_value": 8,
                "time_criticality": 5,
                "risk_reduction": 3,
                "job_size": 5,
                "status": "New",
                "owner": "Alice Johnson",
                "team": "Security Team",
                "program_increment_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    }


class WSJFItemUpdate(BaseModel):
    subject: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    business_value: int | None = Field(None)
    time_criticality: int | None = Field(None)
    risk_reduction: int | None = Field(None)
    job_size: int | None = Field(None)
    status: WSJFStatus | None = None
    owner: str | None = Field(None, max_length=100)
    team: str | None = Field(None, max_length=100)
    program_increment_id: UUID | None = Field(None, description="Program Increment UUID reference")

    @field_validator("business_value", "time_criticality", "risk_reduction", "job_size")
    @classmethod
    def validate_fibonacci_values(cls, v: int | None) -> int | None:
        """Validate that optional score values are valid Fibonacci numbers.

        Args:
            v (int | None): The optional score value to validate.

        Returns:
            int | None: The validated score value or None.

        Raises:
            ValueError: If score is not a valid Fibonacci value.
        """
        if v is not None and v not in FIBONACCI_VALUES:
            raise ValueError(f"Score must be one of {FIBONACCI_VALUES}")
        return v


class WSJFItem(WSJFItemBase):
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    created_date: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    @computed_field
    @property
    def wsjf_score(self) -> float:
        """Calculate WSJF score: (Business Value + Time Criticality + Risk Reduction) / Job Size.

        Returns:
            float: The calculated WSJF score rounded to 2 decimal places.
        """
        return round(
            (self.business_value + self.time_criticality + self.risk_reduction)
            / self.job_size,
            2,
        )

    class Config:
        from_attributes = True


class WSJFItemResponse(WSJFItem):
    priority: int | None = Field(None, description="Priority rank based on WSJF score")


class WSJFItemBatch(BaseModel):
    items: list[WSJFItemCreate] = Field(..., description="List of WSJF items to create")

    @field_validator("items")
    @classmethod
    def validate_items_not_empty(cls, v: list[WSJFItemCreate]) -> list[WSJFItemCreate]:
        """Validate that batch contains between 1 and 100 items.

        Args:
            v (list[WSJFItemCreate]): The list of items to validate.

        Returns:
            list[WSJFItemCreate]: The validated list of items.

        Raises:
            ValueError: If list is empty or contains more than 100 items.
        """
        if len(v) == 0:
            raise ValueError("At least one item is required")
        if len(v) > 100:
            raise ValueError("Maximum 100 items allowed per batch")
        return v
