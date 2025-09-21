from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, computed_field, field_validator

from .status import WSJFStatus


# Sub-value structure for WSJF components
class WSJFSubValues(BaseModel):
    pms_business: int | None = None
    pos_business: int | None = None
    bos_agri_business: int | None = None
    bos_cabinet_business: int | None = None
    consultants_business: int | None = None
    dev_business: int | None = None
    dev_technical: int | None = None
    ia_business: int | None = None
    ia_technical: int | None = None
    devops_business: int | None = None
    devops_technical: int | None = None
    support_business: int | None = None

    def calculate_max_value(self) -> int:
        """Calculate the maximum value from all non-null sub-values."""
        values = [v for v in self.model_dump().values() if v is not None]
        return max(values) if values else 0

    @field_validator("*")
    @classmethod
    def validate_fibonacci_values(cls, v: int | None) -> int | None:
        """Validate that all values are valid Fibonacci numbers when not None."""
        if v is not None and v not in FIBONACCI_VALUES:
            raise ValueError(f"Values must be one of {FIBONACCI_VALUES}")
        return v


# Fibonacci values for job size estimation
FIBONACCI_VALUES = [1, 2, 3, 5, 8, 13, 21]


class WSJFItemBase(BaseModel):
    subject: str = Field(
        ..., min_length=1, max_length=200, description="Feature/requirement name"
    )
    description: str = Field("", max_length=1000, description="Detailed explanation")
    business_value: WSJFSubValues = Field(
        ..., description="Sub-values for business value assessment"
    )
    time_criticality: WSJFSubValues = Field(
        ..., description="Sub-values for time criticality assessment"
    )
    risk_reduction: WSJFSubValues = Field(
        ..., description="Sub-values for risk reduction assessment"
    )
    job_size: int = Field(
        ..., description="Effort required (Fibonacci: 1,2,3,5,8,13,21)"
    )
    status: WSJFStatus = Field(WSJFStatus.NEW, description="Current state")
    owner: str | None = Field(None, max_length=100, description="Responsible person")
    team: str | None = Field(None, max_length=100, description="Assigned team")
    program_increment_id: UUID = Field(
        ..., description="Program Increment UUID reference"
    )

    @field_validator("business_value", "time_criticality", "risk_reduction")
    @classmethod
    def validate_at_least_one_value(cls, v: WSJFSubValues) -> WSJFSubValues:
        """Validate that at least one sub-value is set.

        Args:
            v (WSJFSubValues): The sub-values to validate.

        Returns:
            WSJFSubValues: The validated sub-values.

        Raises:
            ValueError: If no sub-values are set.
        """
        if v.calculate_max_value() == 0:
            raise ValueError("At least one sub-value must be set")
        return v

    @field_validator("job_size")
    @classmethod
    def validate_job_size_fibonacci(cls, v: int) -> int:
        """Validate that job size is a valid Fibonacci number.

        Args:
            v (int): The job size value to validate.

        Returns:
            int: The validated job size value.

        Raises:
            ValueError: If job size is not a valid Fibonacci value.
        """
        if v not in FIBONACCI_VALUES:
            raise ValueError(f"Job size must be one of {FIBONACCI_VALUES}")
        return v


class WSJFItemCreate(WSJFItemBase):
    model_config = {
        "json_schema_extra": {
            "example": {
                "subject": "User Authentication System",
                "description": "Implement secure login and registration with OAuth2",
                "business_value": {"dev_technical": 13, "ia_business": 8},
                "time_criticality": {"pms_business": 21, "consultants_business": 5},
                "risk_reduction": {"dev_business": 8, "support_business": 3},
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
    business_value: WSJFSubValues | None = Field(None)
    time_criticality: WSJFSubValues | None = Field(None)
    risk_reduction: WSJFSubValues | None = Field(None)
    job_size: int | None = Field(None)
    status: WSJFStatus | None = None
    owner: str | None = Field(None, max_length=100)
    team: str | None = Field(None, max_length=100)
    program_increment_id: UUID | None = Field(
        None, description="Program Increment UUID reference"
    )

    @field_validator("job_size")
    @classmethod
    def validate_job_size_fibonacci(cls, v: int | None) -> int | None:
        """Validate that optional job size is a valid Fibonacci number.

        Args:
            v (int | None): The optional job size value to validate.

        Returns:
            int | None: The validated job size value or None.

        Raises:
            ValueError: If job size is not a valid Fibonacci value.
        """
        if v is not None and v not in FIBONACCI_VALUES:
            raise ValueError(f"Job size must be one of {FIBONACCI_VALUES}")
        return v


class WSJFItem(WSJFItemBase):
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    created_date: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    @computed_field
    def wsjf_score(self) -> float:
        """Calculate WSJF score: (Business Value + Time Criticality + Risk Reduction) / Job Size.

        Uses the maximum value from each component's sub-values.

        Returns:
            float: The calculated WSJF score rounded to 2 decimal places.
        """
        business_score = self.business_value.calculate_max_value()
        time_score = self.time_criticality.calculate_max_value()
        risk_score = self.risk_reduction.calculate_max_value()

        return round(
            (business_score + time_score + risk_score) / self.job_size,
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
