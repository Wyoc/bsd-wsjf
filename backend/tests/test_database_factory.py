"""Tests for database factory and PostgreSQL integration."""

import uuid
from datetime import UTC, datetime

from app.core.database_factory import DatabaseConnection, DatabaseManager


class TestDatabaseConnection:
    """Test DatabaseConnection functionality."""

    def test_connection_creation(self, db_connection: DatabaseConnection):
        """Test that database connection is created successfully."""
        assert db_connection is not None
        assert hasattr(db_connection, "connection")

    def test_execute_query(self, db_connection: DatabaseConnection):
        """Test executing a simple query."""
        # This should not raise an exception
        db_connection.execute("SELECT 1")

    def test_fetchone_query(self, db_connection: DatabaseConnection):
        """Test fetchone with a simple query."""
        result = db_connection.fetchone("SELECT %(value)s as test_value", {"value": 42})
        assert result is not None
        assert result["test_value"] == 42

    def test_fetchall_query(self, db_connection: DatabaseConnection):
        """Test fetchall with a simple query."""
        results = db_connection.fetchall(
            "SELECT %(value1)s as val1, %(value2)s as val2", {"value1": 1, "value2": 2}
        )
        assert len(results) == 1
        assert results[0]["val1"] == 1
        assert results[0]["val2"] == 2

    def test_parameterized_query(self, db_connection: DatabaseConnection):
        """Test parameterized queries work correctly."""
        test_value = "test_string"
        result = db_connection.fetchone(
            "SELECT %(input)s as output", {"input": test_value}
        )
        assert result["output"] == test_value

    def test_commit_rollback(self, db_connection: DatabaseConnection):
        """Test transaction control."""
        # Create a test table
        db_connection.execute("""
            CREATE TEMPORARY TABLE test_commit_table (
                id SERIAL PRIMARY KEY,
                value TEXT
            )
        """)

        # Insert data and commit
        db_connection.execute(
            "INSERT INTO test_commit_table (value) VALUES (%(val)s)",
            {"val": "test_value"},
        )
        db_connection.commit()

        # Verify data exists
        result = db_connection.fetchone(
            "SELECT value FROM test_commit_table WHERE value = %(val)s",
            {"val": "test_value"},
        )
        assert result is not None
        assert result["value"] == "test_value"

        # Test rollback
        db_connection.execute(
            "INSERT INTO test_commit_table (value) VALUES (%(val)s)",
            {"val": "rollback_test"},
        )
        db_connection.rollback()

        # Verify rollback worked
        result = db_connection.fetchone(
            "SELECT value FROM test_commit_table WHERE value = %(val)s",
            {"val": "rollback_test"},
        )
        assert result is None


class TestDatabaseManager:
    """Test DatabaseManager functionality."""

    def test_manager_singleton_behavior(self, clean_database: DatabaseManager):
        """Test that manager maintains connection properly."""
        conn1 = clean_database.connect()
        conn2 = clean_database.connect()

        # Should return the same connection
        assert conn1 is conn2

    def test_context_manager(self, clean_database: DatabaseManager):
        """Test context manager functionality."""
        with clean_database as conn:
            assert isinstance(conn, DatabaseConnection)
            result = conn.fetchone("SELECT 1 as test")
            assert result["test"] == 1


class TestDatabaseSchema:
    """Test database schema creation and structure."""

    def test_program_increments_table_exists(self, db_connection: DatabaseConnection):
        """Test that program_increments table is created correctly."""
        result = db_connection.fetchone("""
            SELECT COUNT(*) as count
            FROM information_schema.tables
            WHERE table_name = 'program_increments'
        """)
        assert result["count"] == 1

    def test_wsjf_items_table_exists(self, db_connection: DatabaseConnection):
        """Test that wsjf_items table is created correctly."""
        result = db_connection.fetchone("""
            SELECT COUNT(*) as count
            FROM information_schema.tables
            WHERE table_name = 'wsjf_items'
        """)
        assert result["count"] == 1

    def test_program_increments_table_structure(
        self, db_connection: DatabaseConnection
    ):
        """Test program_increments table has correct columns."""
        columns = db_connection.fetchall("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'program_increments'
            ORDER BY ordinal_position
        """)

        expected_columns = {
            "id": "uuid",
            "name": "character varying",
            "description": "character varying",
            "start_date": "timestamp without time zone",
            "end_date": "timestamp without time zone",
            "status": "character varying",
            "created_date": "timestamp without time zone",
        }

        actual_columns = {col["column_name"]: col["data_type"] for col in columns}

        for col_name, col_type in expected_columns.items():
            assert col_name in actual_columns
            assert actual_columns[col_name] == col_type

    def test_wsjf_items_table_structure(self, db_connection: DatabaseConnection):
        """Test wsjf_items table has correct columns."""
        columns = db_connection.fetchall("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'wsjf_items'
            ORDER BY ordinal_position
        """)

        expected_columns = {
            "id": "uuid",
            "subject": "character varying",
            "description": "character varying",
            "business_value": "jsonb",
            "time_criticality": "jsonb",
            "risk_reduction": "jsonb",
            "job_size": "jsonb",
            "status": "character varying",
            "owner": "character varying",
            "team": "character varying",
            "program_increment_id": "uuid",
            "created_date": "timestamp without time zone",
        }

        actual_columns = {col["column_name"]: col["data_type"] for col in columns}

        for col_name, col_type in expected_columns.items():
            assert col_name in actual_columns
            assert actual_columns[col_name] == col_type

    def test_foreign_key_constraints(self, db_connection: DatabaseConnection):
        """Test that foreign key constraints exist."""
        constraints = db_connection.fetchall("""
            SELECT constraint_name, table_name, column_name, foreign_table_name, foreign_column_name
            FROM information_schema.key_column_usage kcu
            JOIN information_schema.referential_constraints rc
                ON kcu.constraint_name = rc.constraint_name
            JOIN information_schema.key_column_usage fkcu
                ON rc.unique_constraint_name = fkcu.constraint_name
            WHERE kcu.table_name = 'wsjf_items'
        """)

        assert len(constraints) >= 1
        # Should have foreign key from wsjf_items.program_increment_id to program_increments.id


class TestDatabaseOperations:
    """Test basic CRUD operations on database."""

    def test_insert_and_select_program_increment(
        self, db_connection: DatabaseConnection
    ):
        """Test inserting and selecting a program increment."""
        pi_id = str(uuid.uuid4())
        pi_name = "Test PI"
        start_date = datetime.now(UTC)
        end_date = datetime.now(UTC)

        # Insert PI
        db_connection.execute(
            """
            INSERT INTO program_increments (id, name, description, start_date, end_date, status)
            VALUES (%(id)s, %(name)s, %(description)s, %(start_date)s, %(end_date)s, %(status)s)
        """,
            {
                "id": pi_id,
                "name": pi_name,
                "description": "Test description",
                "start_date": start_date,
                "end_date": end_date,
                "status": "Planning",
            },
        )
        db_connection.commit()

        # Select and verify
        result = db_connection.fetchone(
            "SELECT * FROM program_increments WHERE id = %(id)s", {"id": pi_id}
        )

        assert result is not None
        assert result["name"] == pi_name
        assert result["status"] == "Planning"

    def test_insert_and_select_wsjf_item(self, db_connection: DatabaseConnection):
        """Test inserting and selecting a WSJF item."""
        # First create a PI
        pi_id = str(uuid.uuid4())
        db_connection.execute(
            """
            INSERT INTO program_increments (id, name, description, start_date, end_date, status)
            VALUES (%(id)s, %(name)s, %(description)s, %(start_date)s, %(end_date)s, %(status)s)
        """,
            {
                "id": pi_id,
                "name": "Test PI",
                "description": "Test description",
                "start_date": datetime.now(UTC),
                "end_date": datetime.now(UTC),
                "status": "Planning",
            },
        )

        # Insert WSJF item
        item_id = str(uuid.uuid4())
        business_value = {"pms_business": 21, "dev_technical": 13}

        db_connection.execute(
            """
            INSERT INTO wsjf_items (
                id, subject, description, business_value, time_criticality,
                risk_reduction, job_size, status, owner, team, program_increment_id
            ) VALUES (
                %(id)s, %(subject)s, %(description)s, %(business_value)s, %(time_criticality)s,
                %(risk_reduction)s, %(job_size)s, %(status)s, %(owner)s, %(team)s, %(program_increment_id)s
            )
        """,
            {
                "id": item_id,
                "subject": "Test Item",
                "description": "Test description",
                "business_value": business_value,
                "time_criticality": {"consultants_business": 5},
                "risk_reduction": {"dev_business": 8},
                "job_size": {"dev": 5, "ia": 3},
                "status": "New",
                "owner": "Test Owner",
                "team": "Test Team",
                "program_increment_id": pi_id,
            },
        )
        db_connection.commit()

        # Select and verify
        result = db_connection.fetchone(
            "SELECT * FROM wsjf_items WHERE id = %(id)s", {"id": item_id}
        )

        assert result is not None
        assert result["subject"] == "Test Item"
        assert result["business_value"]["pms_business"] == 21
        assert result["business_value"]["dev_technical"] == 13

    def test_jsonb_operations(self, db_connection: DatabaseConnection):
        """Test JSONB operations and queries."""
        # Create PI first
        pi_id = str(uuid.uuid4())
        db_connection.execute(
            """
            INSERT INTO program_increments (id, name, description, start_date, end_date, status)
            VALUES (%(id)s, %(name)s, %(description)s, %(start_date)s, %(end_date)s, %(status)s)
        """,
            {
                "id": pi_id,
                "name": "Test PI",
                "description": "Test",
                "start_date": datetime.now(UTC),
                "end_date": datetime.now(UTC),
                "status": "Planning",
            },
        )

        # Insert item with complex JSONB data
        item_id = str(uuid.uuid4())
        business_value = {
            "pms_business": 21,
            "dev_technical": 13,
            "ia_business": 8,
            "pos_business": None,
        }

        db_connection.execute(
            """
            INSERT INTO wsjf_items (
                id, subject, business_value, time_criticality, risk_reduction,
                job_size, program_increment_id
            ) VALUES (
                %(id)s, %(subject)s, %(business_value)s, %(time_criticality)s,
                %(risk_reduction)s, %(job_size)s, %(program_increment_id)s
            )
        """,
            {
                "id": item_id,
                "subject": "JSONB Test",
                "business_value": business_value,
                "time_criticality": {"consultants_business": 5},
                "risk_reduction": {"dev_business": 8},
                "job_size": {"dev": 5},
                "program_increment_id": pi_id,
            },
        )
        db_connection.commit()

        # Test JSONB queries
        result = db_connection.fetchone(
            """
            SELECT business_value->'pms_business' as pms_value,
                   business_value->'pos_business' as pos_value
            FROM wsjf_items WHERE id = %(id)s
        """,
            {"id": item_id},
        )

        assert result["pms_value"] == 21
        assert result["pos_value"] is None

    def test_cascade_delete(self, db_connection: DatabaseConnection):
        """Test that deleting PI cascades to WSJF items."""
        # Create PI
        pi_id = str(uuid.uuid4())
        db_connection.execute(
            """
            INSERT INTO program_increments (id, name, description, start_date, end_date, status)
            VALUES (%(id)s, %(name)s, %(description)s, %(start_date)s, %(end_date)s, %(status)s)
        """,
            {
                "id": pi_id,
                "name": "Cascade Test PI",
                "description": "Test",
                "start_date": datetime.now(UTC),
                "end_date": datetime.now(UTC),
                "status": "Planning",
            },
        )

        # Create WSJF item
        item_id = str(uuid.uuid4())
        db_connection.execute(
            """
            INSERT INTO wsjf_items (
                id, subject, business_value, time_criticality, risk_reduction,
                job_size, program_increment_id
            ) VALUES (
                %(id)s, %(subject)s, %(business_value)s, %(time_criticality)s,
                %(risk_reduction)s, %(job_size)s, %(program_increment_id)s
            )
        """,
            {
                "id": item_id,
                "subject": "Cascade Test Item",
                "business_value": {"pms_business": 5},
                "time_criticality": {"consultants_business": 5},
                "risk_reduction": {"dev_business": 3},
                "job_size": {"dev": 2},
                "program_increment_id": pi_id,
            },
        )
        db_connection.commit()

        # Verify item exists
        result = db_connection.fetchone(
            "SELECT COUNT(*) as count FROM wsjf_items WHERE program_increment_id = %(id)s",
            {"id": pi_id},
        )
        assert result["count"] == 1

        # Delete PI
        db_connection.execute(
            "DELETE FROM program_increments WHERE id = %(id)s", {"id": pi_id}
        )
        db_connection.commit()

        # Verify item was cascade deleted
        result = db_connection.fetchone(
            "SELECT COUNT(*) as count FROM wsjf_items WHERE program_increment_id = %(id)s",
            {"id": pi_id},
        )
        assert result["count"] == 0
