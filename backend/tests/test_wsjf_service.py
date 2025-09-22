"""Tests for WSJF service functionality."""

from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.models import ProgramIncrement, WSJFItemCreate, WSJFItemUpdate
from app.models.wsjf_item import JobSizeSubValues, WSJFSubValues
from app.services.wsjf_service import WSJFService


class TestWSJFService:
    """Test WSJF service functionality."""

    @pytest.fixture
    def wsjf_service(self, clean_database):
        """Create WSJF service with clean database."""
        service = WSJFService()
        # Override database manager with test instance
        service.db = clean_database
        return service

    @pytest.fixture
    def sample_pi(self, clean_database):
        """Create a sample program increment for testing."""
        pi = ProgramIncrement(
            name="Test PI",
            description="Test Program Increment",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC),
            status="Planning",
        )

        conn = clean_database.connect()
        conn.execute(
            """
            INSERT INTO program_increments (
                id, name, description, start_date, end_date, status, created_date
            ) VALUES (%(id)s, %(name)s, %(description)s, %(start_date)s, %(end_date)s, %(status)s, %(created_date)s)
        """,
            {
                "id": str(pi.id),
                "name": pi.name,
                "description": pi.description,
                "start_date": pi.start_date,
                "end_date": pi.end_date,
                "status": pi.status,
                "created_date": pi.created_date,
            },
        )
        conn.commit()

        return pi

    @pytest.fixture
    def sample_wsjf_item_data(self, sample_pi):
        """Create sample WSJF item data."""
        return WSJFItemCreate(
            subject="Test Authentication System",
            description="Implement secure login system",
            business_value=WSJFSubValues(
                pms_business=21, dev_technical=13, ia_business=8
            ),
            time_criticality=WSJFSubValues(consultants_business=13, support_business=5),
            risk_reduction=WSJFSubValues(dev_business=8, devops_technical=3),
            job_size=JobSizeSubValues(dev=5, ia=3, devops=2, exploit=1),
            owner="Test Owner",
            team="Test Team",
            program_increment_id=sample_pi.id,
        )

    def test_create_item(self, wsjf_service, sample_wsjf_item_data):
        """Test creating a WSJF item."""
        created_item = wsjf_service.create_item(sample_wsjf_item_data)

        assert created_item is not None
        assert isinstance(created_item.id, UUID)
        assert created_item.subject == sample_wsjf_item_data.subject
        assert created_item.description == sample_wsjf_item_data.description
        assert created_item.owner == sample_wsjf_item_data.owner
        assert created_item.team == sample_wsjf_item_data.team
        assert (
            created_item.program_increment_id
            == sample_wsjf_item_data.program_increment_id
        )

        # Test sub-values
        assert created_item.business_value.pms_business == 21
        assert created_item.business_value.dev_technical == 13
        assert created_item.time_criticality.consultants_business == 13
        assert created_item.job_size.dev == 5

        # Test WSJF score calculation
        expected_score = (21 + 13 + 8) / 5  # max values from each component
        assert abs(created_item.wsjf_score - expected_score) < 0.01

    def test_get_item(self, wsjf_service, sample_wsjf_item_data):
        """Test retrieving a WSJF item by ID."""
        # Create item first
        created_item = wsjf_service.create_item(sample_wsjf_item_data)

        # Retrieve item
        retrieved_item = wsjf_service.get_item(created_item.id)

        assert retrieved_item is not None
        assert retrieved_item.id == created_item.id
        assert retrieved_item.subject == created_item.subject
        assert (
            retrieved_item.business_value.pms_business
            == created_item.business_value.pms_business
        )

    def test_get_item_not_found(self, wsjf_service):
        """Test retrieving non-existent item returns None."""
        from uuid import uuid4

        non_existent_id = uuid4()

        result = wsjf_service.get_item(non_existent_id)
        assert result is None

    def test_get_all_items(self, wsjf_service, sample_wsjf_item_data):
        """Test retrieving all WSJF items."""
        # Create multiple items
        item1 = wsjf_service.create_item(sample_wsjf_item_data)

        item2_data = sample_wsjf_item_data.model_copy()
        item2_data.subject = "Second Test Item"
        item2_data.business_value.pms_business = 8  # Lower score
        item2 = wsjf_service.create_item(item2_data)

        # Retrieve all items
        all_items = wsjf_service.get_all_items()

        assert len(all_items) == 2

        # Items should be sorted by priority (WSJF score descending)
        assert all_items[0].priority == 1
        assert all_items[1].priority == 2

        # Higher WSJF score should be first
        assert all_items[0].wsjf_score > all_items[1].wsjf_score
        assert all_items[0].id == item1.id
        assert all_items[1].id == item2.id

    def test_get_items_by_program_increment(
        self, wsjf_service, sample_wsjf_item_data, sample_pi
    ):
        """Test filtering items by program increment."""
        # Create item in sample PI
        item1 = wsjf_service.create_item(sample_wsjf_item_data)

        # Create another PI and item
        from app.models import ProgramIncrement

        other_pi = ProgramIncrement(
            name="Other PI",
            description="Other Program Increment",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC),
            status="Planning",
        )

        conn = wsjf_service.db.connect()
        conn.execute(
            """
            INSERT INTO program_increments (
                id, name, description, start_date, end_date, status, created_date
            ) VALUES (%(id)s, %(name)s, %(description)s, %(start_date)s, %(end_date)s, %(status)s, %(created_date)s)
        """,
            {
                "id": str(other_pi.id),
                "name": other_pi.name,
                "description": other_pi.description,
                "start_date": other_pi.start_date,
                "end_date": other_pi.end_date,
                "status": other_pi.status,
                "created_date": other_pi.created_date,
            },
        )
        conn.commit()

        item2_data = sample_wsjf_item_data.model_copy()
        item2_data.subject = "Other PI Item"
        item2_data.program_increment_id = other_pi.id
        item2 = wsjf_service.create_item(item2_data)

        # Test filtering by sample PI
        sample_pi_items = wsjf_service.get_all_items(sample_pi.id)
        assert len(sample_pi_items) == 1
        assert sample_pi_items[0].id == item1.id

        # Test filtering by other PI
        other_pi_items = wsjf_service.get_all_items(other_pi.id)
        assert len(other_pi_items) == 1
        assert other_pi_items[0].id == item2.id

        # Test getting all items (no filter)
        all_items = wsjf_service.get_all_items()
        assert len(all_items) == 2

    def test_update_item(self, wsjf_service, sample_wsjf_item_data):
        """Test updating a WSJF item."""
        # Create item
        created_item = wsjf_service.create_item(sample_wsjf_item_data)

        # Update item
        update_data = WSJFItemUpdate(
            subject="Updated Subject",
            description="Updated Description",
            business_value=WSJFSubValues(pms_business=8, dev_technical=5),
            status="Go",
        )

        updated_item = wsjf_service.update_item(created_item.id, update_data)

        assert updated_item is not None
        assert updated_item.id == created_item.id
        assert updated_item.subject == "Updated Subject"
        assert updated_item.description == "Updated Description"
        assert updated_item.business_value.pms_business == 8
        assert updated_item.business_value.dev_technical == 5
        assert updated_item.status.value == "Go"

        # Unchanged fields should remain the same
        assert updated_item.owner == created_item.owner
        assert updated_item.team == created_item.team

    def test_update_item_not_found(self, wsjf_service):
        """Test updating non-existent item returns None."""
        from uuid import uuid4

        non_existent_id = uuid4()

        update_data = WSJFItemUpdate(subject="Updated Subject")
        result = wsjf_service.update_item(non_existent_id, update_data)
        assert result is None

    def test_update_item_empty_data(self, wsjf_service, sample_wsjf_item_data):
        """Test updating with empty data returns unchanged item."""
        # Create item
        created_item = wsjf_service.create_item(sample_wsjf_item_data)

        # Update with empty data
        update_data = WSJFItemUpdate()
        updated_item = wsjf_service.update_item(created_item.id, update_data)

        assert updated_item is not None
        assert updated_item.subject == created_item.subject
        assert updated_item.description == created_item.description

    def test_delete_item(self, wsjf_service, sample_wsjf_item_data):
        """Test deleting a WSJF item."""
        # Create item
        created_item = wsjf_service.create_item(sample_wsjf_item_data)

        # Verify item exists
        retrieved_item = wsjf_service.get_item(created_item.id)
        assert retrieved_item is not None

        # Delete item
        result = wsjf_service.delete_item(created_item.id)
        assert result is True

        # Verify item is deleted
        deleted_item = wsjf_service.get_item(created_item.id)
        assert deleted_item is None

    def test_delete_item_not_found(self, wsjf_service):
        """Test deleting non-existent item."""
        from uuid import uuid4

        non_existent_id = uuid4()

        result = wsjf_service.delete_item(non_existent_id)
        assert (
            result is True
        )  # Our implementation returns True even if item doesn't exist

    def test_create_batch(self, wsjf_service, sample_wsjf_item_data):
        """Test creating multiple WSJF items in batch."""
        # Create batch data
        item1_data = sample_wsjf_item_data

        item2_data = sample_wsjf_item_data.model_copy()
        item2_data.subject = "Second Batch Item"
        item2_data.business_value.pms_business = 8

        item3_data = sample_wsjf_item_data.model_copy()
        item3_data.subject = "Third Batch Item"
        item3_data.business_value.pms_business = 13

        batch_data = [item1_data, item2_data, item3_data]

        # Create batch
        created_items = wsjf_service.create_batch(batch_data)

        assert len(created_items) == 3

        # Verify all items have unique IDs
        ids = [item.id for item in created_items]
        assert len(set(ids)) == 3

        # Verify items were saved to database
        all_items = wsjf_service.get_all_items()
        assert len(all_items) == 3

    def test_get_sample_data(self, wsjf_service):
        """Test generating sample data."""
        sample_items = wsjf_service.get_sample_data()

        assert len(sample_items) == 3

        # Verify items have priorities
        priorities = [item.priority for item in sample_items]
        assert set(priorities) == {1, 2, 3}

        # Verify PI was created
        all_pis = wsjf_service.db.connect().fetchall("SELECT * FROM program_increments")
        assert len(all_pis) >= 1

        pi18_exists = any(pi["name"] == "PI18" for pi in all_pis)
        assert pi18_exists

    def test_get_sample_data_idempotent(self, wsjf_service):
        """Test that calling get_sample_data multiple times is idempotent."""
        # First call
        sample_items1 = wsjf_service.get_sample_data()
        assert len(sample_items1) == 3

        # Second call should replace data
        sample_items2 = wsjf_service.get_sample_data()
        assert len(sample_items2) == 3

        # Should only have 3 items total (not 6)
        all_items = wsjf_service.get_all_items()
        assert len(all_items) == 3

    def test_wsjf_score_calculation(self, wsjf_service, sample_pi):
        """Test WSJF score calculation with different values."""
        # Create item with specific values for testing
        item_data = WSJFItemCreate(
            subject="Score Test Item",
            description="Test WSJF score calculation",
            business_value=WSJFSubValues(
                pms_business=21,  # Max: 21
                dev_technical=13,
                ia_business=8,
            ),
            time_criticality=WSJFSubValues(
                consultants_business=5,  # Max: 5
                support_business=3,
            ),
            risk_reduction=WSJFSubValues(
                dev_business=8,  # Max: 8
                devops_technical=3,
            ),
            job_size=JobSizeSubValues(
                dev=5,  # Max: 5
                ia=3,
                devops=2,
                exploit=1,
            ),
            program_increment_id=sample_pi.id,
        )

        created_item = wsjf_service.create_item(item_data)

        # Expected WSJF = (21 + 5 + 8) / 5 = 34 / 5 = 6.8
        expected_score = 6.8
        assert abs(created_item.wsjf_score - expected_score) < 0.01

    def test_priority_ranking(self, wsjf_service, sample_pi):
        """Test that items are ranked correctly by WSJF score."""
        # Create items with different WSJF scores
        high_score_item = WSJFItemCreate(
            subject="High Score Item",
            business_value=WSJFSubValues(pms_business=21),
            time_criticality=WSJFSubValues(consultants_business=21),
            risk_reduction=WSJFSubValues(dev_business=21),
            job_size=JobSizeSubValues(dev=1),  # Small job = high score
            program_increment_id=sample_pi.id,
        )

        medium_score_item = WSJFItemCreate(
            subject="Medium Score Item",
            business_value=WSJFSubValues(pms_business=13),
            time_criticality=WSJFSubValues(consultants_business=13),
            risk_reduction=WSJFSubValues(dev_business=13),
            job_size=JobSizeSubValues(dev=3),
            program_increment_id=sample_pi.id,
        )

        low_score_item = WSJFItemCreate(
            subject="Low Score Item",
            business_value=WSJFSubValues(pms_business=5),
            time_criticality=WSJFSubValues(consultants_business=5),
            risk_reduction=WSJFSubValues(dev_business=5),
            job_size=JobSizeSubValues(dev=8),  # Large job = low score
            program_increment_id=sample_pi.id,
        )

        # Create items in random order
        wsjf_service.create_item(medium_score_item)
        wsjf_service.create_item(low_score_item)
        wsjf_service.create_item(high_score_item)

        # Get all items (should be sorted by WSJF score)
        all_items = wsjf_service.get_all_items()

        assert len(all_items) == 3
        assert all_items[0].subject == "High Score Item"
        assert all_items[0].priority == 1
        assert all_items[1].subject == "Medium Score Item"
        assert all_items[1].priority == 2
        assert all_items[2].subject == "Low Score Item"
        assert all_items[2].priority == 3

        # Verify WSJF scores are in descending order
        assert all_items[0].wsjf_score > all_items[1].wsjf_score
        assert all_items[1].wsjf_score > all_items[2].wsjf_score
