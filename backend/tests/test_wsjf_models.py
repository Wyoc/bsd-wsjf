from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models import WSJFItemCreate, WSJFStatus, WSJFSubValues


def test_wsjf_item_create_valid():
    """Test creating a valid WSJF item.

    Tests that a WSJF item can be created with valid data and that
    all fields are properly set, including default values.
    """
    item = WSJFItemCreate(
        subject="Test Feature",
        description="Test description",
        business_value=WSJFSubValues(dev_business=8),
        time_criticality=WSJFSubValues(pms_business=5),
        risk_reduction=WSJFSubValues(support_business=3),
        job_size=5,
        program_increment_id=uuid4(),
    )

    assert item.subject == "Test Feature"
    assert item.business_value.calculate_max_value() == 8
    assert item.status == WSJFStatus.NEW


def test_wsjf_item_score_validation():
    """Test score validation (must be Fibonacci values).

    Tests that ValidationError is raised when score values
    are not valid Fibonacci numbers.
    """
    with pytest.raises(ValidationError):
        WSJFSubValues(dev_business=10)  # Invalid: not a Fibonacci number

    with pytest.raises(ValidationError):
        WSJFItemCreate(
            subject="Test",
            business_value=WSJFSubValues(dev_business=8),
            time_criticality=WSJFSubValues(pms_business=5),
            risk_reduction=WSJFSubValues(support_business=3),
            job_size=4,  # Invalid: not a Fibonacci number
            program_increment_id=uuid4(),
        )


def test_wsjf_score_calculation():
    """Test WSJF score calculation.

    Tests that the WSJF score is correctly calculated using the formula:
    (Business Value + Time Criticality + Risk Reduction) / Job Size
    """
    from app.models import WSJFItem

    item = WSJFItem(
        subject="Test Feature",
        business_value=WSJFSubValues(dev_business=8),
        time_criticality=WSJFSubValues(
            pms_business=5, consultants_business=3
        ),  # max = 5
        risk_reduction=WSJFSubValues(support_business=3),
        job_size=5,
        program_increment_id=uuid4(),
    )

    # WSJF = (8 + 5 + 3) / 5 = 16 / 5 = 3.2
    assert item.wsjf_score == 3.2


def test_subject_validation():
    """Test subject field validation.

    Tests that ValidationError is raised when the subject field
    is empty or invalid.
    """
    with pytest.raises(ValidationError):
        WSJFItemCreate(
            subject="",  # Invalid: empty
            business_value=WSJFSubValues(dev_business=8),
            time_criticality=WSJFSubValues(pms_business=5),
            risk_reduction=WSJFSubValues(support_business=3),
            job_size=5,
            program_increment_id=uuid4(),
        )
