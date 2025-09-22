"""Tests for Program Increment service functionality."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from app.models import ProgramIncrementCreate, ProgramIncrementUpdate
from app.services.pi_service import ProgramIncrementService


class TestProgramIncrementService:
    """Test Program Increment service functionality."""

    @pytest.fixture
    def pi_service(self, clean_database):
        """Create PI service with clean database."""
        service = ProgramIncrementService()
        # Override database manager with test instance
        service.db = clean_database
        return service

    @pytest.fixture
    def sample_pi_data(self):
        """Create sample PI data."""
        return ProgramIncrementCreate(
            name="PI19",
            description="Test Program Increment 19",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC) + timedelta(days=90),
            status="Planning",
        )

    def test_create_pi(self, pi_service, sample_pi_data):
        """Test creating a Program Increment."""
        created_pi = pi_service.create_pi(sample_pi_data)

        assert created_pi is not None
        assert isinstance(created_pi.id, UUID)
        assert created_pi.name == sample_pi_data.name
        assert created_pi.description == sample_pi_data.description
        assert created_pi.status == sample_pi_data.status
        assert created_pi.start_date == sample_pi_data.start_date
        assert created_pi.end_date == sample_pi_data.end_date
        assert created_pi.item_count == 0

    def test_create_pi_unique_name_constraint(self, pi_service, sample_pi_data):
        """Test that PI names must be unique."""
        # Create first PI
        pi_service.create_pi(sample_pi_data)

        # Try to create second PI with same name
        duplicate_pi_data = sample_pi_data.model_copy()
        duplicate_pi_data.description = "Different description"

        with pytest.raises(
            (Exception, ValueError)
        ):  # Should raise database constraint violation
            pi_service.create_pi(duplicate_pi_data)

    def test_get_pi(self, pi_service, sample_pi_data):
        """Test retrieving a PI by ID."""
        # Create PI first
        created_pi = pi_service.create_pi(sample_pi_data)

        # Retrieve PI
        retrieved_pi = pi_service.get_pi(created_pi.id)

        assert retrieved_pi is not None
        assert retrieved_pi.id == created_pi.id
        assert retrieved_pi.name == created_pi.name
        assert retrieved_pi.description == created_pi.description
        assert retrieved_pi.status == created_pi.status

    def test_get_pi_not_found(self, pi_service):
        """Test retrieving non-existent PI returns None."""
        from uuid import uuid4

        non_existent_id = uuid4()

        result = pi_service.get_pi(non_existent_id)
        assert result is None

    def test_get_pi_by_name(self, pi_service, sample_pi_data):
        """Test retrieving a PI by name."""
        # Create PI first
        created_pi = pi_service.create_pi(sample_pi_data)

        # Retrieve PI by name
        retrieved_pi = pi_service.get_pi_by_name(created_pi.name)

        assert retrieved_pi is not None
        assert retrieved_pi.id == created_pi.id
        assert retrieved_pi.name == created_pi.name

    def test_get_pi_by_name_not_found(self, pi_service):
        """Test retrieving non-existent PI by name returns None."""
        result = pi_service.get_pi_by_name("NonExistentPI")
        assert result is None

    def test_get_all_pis_empty(self, pi_service):
        """Test retrieving all PIs when none exist."""
        all_pis = pi_service.get_all_pis()
        assert all_pis == []

    def test_get_all_pis(self, pi_service):
        """Test retrieving all PIs."""
        # Create multiple PIs
        pi1_data = ProgramIncrementCreate(
            name="PI18",
            description="First PI",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC) + timedelta(days=90),
            status="Active",
        )

        pi2_data = ProgramIncrementCreate(
            name="PI19",
            description="Second PI",
            start_date=datetime.now(UTC) + timedelta(days=91),
            end_date=datetime.now(UTC) + timedelta(days=181),
            status="Planning",
        )

        created_pi1 = pi_service.create_pi(pi1_data)
        created_pi2 = pi_service.create_pi(pi2_data)

        # Retrieve all PIs
        all_pis = pi_service.get_all_pis()

        assert len(all_pis) == 2

        # Should be ordered by created_date DESC (newest first)
        assert all_pis[0].id == created_pi2.id  # PI19 created second
        assert all_pis[1].id == created_pi1.id  # PI18 created first

        # Verify item counts are 0
        assert all_pis[0].item_count == 0
        assert all_pis[1].item_count == 0

    def test_get_all_pis_with_item_counts(self, pi_service):
        """Test that PI item counts are calculated correctly."""
        # Create PI
        pi_data = ProgramIncrementCreate(
            name="PI_With_Items",
            description="PI with WSJF items",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC) + timedelta(days=90),
            status="Active",
        )
        created_pi = pi_service.create_pi(pi_data)

        # Add WSJF items to the PI
        conn = pi_service.db.connect()

        for i in range(3):
            conn.execute(
                """
                INSERT INTO wsjf_items (
                    id, subject, business_value, time_criticality, risk_reduction,
                    job_size, program_increment_id
                ) VALUES (
                    gen_random_uuid(), %(subject)s, %(business_value)s, %(time_criticality)s,
                    %(risk_reduction)s, %(job_size)s, %(program_increment_id)s
                )
            """,
                {
                    "subject": f"Test Item {i + 1}",
                    "business_value": {"pms_business": 5},
                    "time_criticality": {"consultants_business": 5},
                    "risk_reduction": {"dev_business": 3},
                    "job_size": {"dev": 2},
                    "program_increment_id": str(created_pi.id),
                },
            )
        conn.commit()

        # Retrieve all PIs
        all_pis = pi_service.get_all_pis()

        assert len(all_pis) == 1
        assert all_pis[0].item_count == 3

    def test_update_pi(self, pi_service, sample_pi_data):
        """Test updating a Program Increment."""
        # Create PI
        created_pi = pi_service.create_pi(sample_pi_data)

        # Update PI
        update_data = ProgramIncrementUpdate(
            name="Updated PI19", description="Updated description", status="Active"
        )

        updated_pi = pi_service.update_pi(created_pi.id, update_data)

        assert updated_pi is not None
        assert updated_pi.id == created_pi.id
        assert updated_pi.name == "Updated PI19"
        assert updated_pi.description == "Updated description"
        assert updated_pi.status == "Active"

        # Unchanged fields should remain the same
        assert updated_pi.start_date == created_pi.start_date
        assert updated_pi.end_date == created_pi.end_date

    def test_update_pi_not_found(self, pi_service):
        """Test updating non-existent PI returns None."""
        from uuid import uuid4

        non_existent_id = uuid4()

        update_data = ProgramIncrementUpdate(name="Updated Name")
        result = pi_service.update_pi(non_existent_id, update_data)
        assert result is None

    def test_update_pi_empty_data(self, pi_service, sample_pi_data):
        """Test updating with empty data returns unchanged PI."""
        # Create PI
        created_pi = pi_service.create_pi(sample_pi_data)

        # Update with empty data
        update_data = ProgramIncrementUpdate()
        updated_pi = pi_service.update_pi(created_pi.id, update_data)

        assert updated_pi is not None
        assert updated_pi.name == created_pi.name
        assert updated_pi.description == created_pi.description
        assert updated_pi.status == created_pi.status

    def test_delete_pi(self, pi_service, sample_pi_data):
        """Test deleting a Program Increment."""
        # Create PI
        created_pi = pi_service.create_pi(sample_pi_data)

        # Verify PI exists
        retrieved_pi = pi_service.get_pi(created_pi.id)
        assert retrieved_pi is not None

        # Delete PI
        result = pi_service.delete_pi(created_pi.id)
        assert result is True

        # Verify PI is deleted
        deleted_pi = pi_service.get_pi(created_pi.id)
        assert deleted_pi is None

    def test_delete_pi_not_found(self, pi_service):
        """Test deleting non-existent PI."""
        from uuid import uuid4

        non_existent_id = uuid4()

        result = pi_service.delete_pi(non_existent_id)
        assert result is False

    def test_delete_pi_cascades_to_items(self, pi_service, sample_pi_data):
        """Test that deleting PI also deletes associated WSJF items."""
        # Create PI
        created_pi = pi_service.create_pi(sample_pi_data)

        # Add WSJF items
        conn = pi_service.db.connect()
        for i in range(2):
            conn.execute(
                """
                INSERT INTO wsjf_items (
                    id, subject, business_value, time_criticality, risk_reduction,
                    job_size, program_increment_id
                ) VALUES (
                    gen_random_uuid(), %(subject)s, %(business_value)s, %(time_criticality)s,
                    %(risk_reduction)s, %(job_size)s, %(program_increment_id)s
                )
            """,
                {
                    "subject": f"Cascade Test Item {i + 1}",
                    "business_value": {"pms_business": 5},
                    "time_criticality": {"consultants_business": 5},
                    "risk_reduction": {"dev_business": 3},
                    "job_size": {"dev": 2},
                    "program_increment_id": str(created_pi.id),
                },
            )
        conn.commit()

        # Verify items exist
        items_before = conn.fetchall(
            "SELECT COUNT(*) as count FROM wsjf_items WHERE program_increment_id = %(id)s",
            {"id": str(created_pi.id)},
        )
        assert items_before[0]["count"] == 2

        # Delete PI
        pi_service.delete_pi(created_pi.id)

        # Verify items were cascade deleted
        items_after = conn.fetchall(
            "SELECT COUNT(*) as count FROM wsjf_items WHERE program_increment_id = %(id)s",
            {"id": str(created_pi.id)},
        )
        assert items_after[0]["count"] == 0

    def test_get_pi_stats_empty_pi(self, pi_service, sample_pi_data):
        """Test getting stats for PI with no items."""
        # Create PI without items
        created_pi = pi_service.create_pi(sample_pi_data)

        stats = pi_service.get_pi_stats(created_pi.id)

        assert stats is not None
        assert stats.pi_id == created_pi.id
        assert stats.pi_name == created_pi.name
        assert stats.total_items == 0
        assert stats.avg_wsjf_score == 0.0
        assert stats.status_distribution == {}
        assert stats.team_distribution == {}

    def test_get_pi_stats_not_found(self, pi_service):
        """Test getting stats for non-existent PI."""
        from uuid import uuid4

        non_existent_id = uuid4()

        stats = pi_service.get_pi_stats(non_existent_id)
        assert stats is None

    def test_get_pi_stats_with_items(self, pi_service, sample_pi_data):
        """Test getting stats for PI with items."""
        # Create PI
        created_pi = pi_service.create_pi(sample_pi_data)

        # Add WSJF items with different statuses and teams
        conn = pi_service.db.connect()

        items_data = [
            {
                "subject": "Item 1",
                "status": "New",
                "team": "Team A",
                "business_value": {"pms_business": 21},
                "time_criticality": {"consultants_business": 13},
                "risk_reduction": {"dev_business": 8},
                "job_size": {"dev": 5},
            },
            {
                "subject": "Item 2",
                "status": "Go",
                "team": "Team A",
                "business_value": {"pms_business": 13},
                "time_criticality": {"consultants_business": 8},
                "risk_reduction": {"dev_business": 5},
                "job_size": {"dev": 3},
            },
            {
                "subject": "Item 3",
                "status": "New",
                "team": "Team B",
                "business_value": {"pms_business": 8},
                "time_criticality": {"consultants_business": 5},
                "risk_reduction": {"dev_business": 3},
                "job_size": {"dev": 2},
            },
        ]

        for item in items_data:
            conn.execute(
                """
                INSERT INTO wsjf_items (
                    id, subject, business_value, time_criticality, risk_reduction,
                    job_size, status, team, program_increment_id
                ) VALUES (
                    gen_random_uuid(), %(subject)s, %(business_value)s, %(time_criticality)s,
                    %(risk_reduction)s, %(job_size)s, %(status)s, %(team)s, %(program_increment_id)s
                )
            """,
                {**item, "program_increment_id": str(created_pi.id)},
            )
        conn.commit()

        stats = pi_service.get_pi_stats(created_pi.id)

        assert stats is not None
        assert stats.pi_id == created_pi.id
        assert stats.pi_name == created_pi.name
        assert stats.total_items == 3

        # Check status distribution
        assert stats.status_distribution["New"] == 2
        assert stats.status_distribution["Go"] == 1

        # Check team distribution
        assert stats.team_distribution["Team A"] == 2
        assert stats.team_distribution["Team B"] == 1

        # Average WSJF score should be calculated
        assert stats.avg_wsjf_score > 0

    def test_pi_date_constraints(self, pi_service):
        """Test that PI date constraints are enforced."""
        # Try to create PI with end_date before start_date
        invalid_pi_data = ProgramIncrementCreate(
            name="Invalid PI",
            description="PI with invalid dates",
            start_date=datetime.now(UTC) + timedelta(days=90),
            end_date=datetime.now(UTC),  # End before start
            status="Planning",
        )

        with pytest.raises(
            (Exception, ValueError)
        ):  # Should raise database constraint violation
            pi_service.create_pi(invalid_pi_data)

    def test_pi_status_constraints(self, pi_service):
        """Test that PI status constraints are enforced."""
        # Try to create PI with invalid status
        invalid_pi_data = ProgramIncrementCreate(
            name="Invalid Status PI",
            description="PI with invalid status",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC) + timedelta(days=90),
            status="InvalidStatus",
        )

        with pytest.raises(
            (Exception, ValueError)
        ):  # Should raise database constraint violation
            pi_service.create_pi(invalid_pi_data)

    def test_row_to_pi_conversion(self, pi_service, sample_pi_data):
        """Test internal _row_to_pi method works correctly."""
        # Create PI
        created_pi = pi_service.create_pi(sample_pi_data)

        # Get raw row from database
        conn = pi_service.db.connect()
        row = conn.fetchone(
            "SELECT * FROM program_increments WHERE id = %(id)s",
            {"id": str(created_pi.id)},
        )

        # Test _row_to_pi conversion
        converted_pi = pi_service._row_to_pi(row)

        assert converted_pi.id == created_pi.id
        assert converted_pi.name == created_pi.name
        assert converted_pi.description == created_pi.description
        assert converted_pi.status == created_pi.status
        assert converted_pi.item_count == 0  # Default value
