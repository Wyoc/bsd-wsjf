"""Test database utilities and fixtures."""

from collections.abc import Generator

import pytest

from app.core.database_factory import DatabaseConnection, DatabaseManager
from app.core.test_config import test_settings


class TestDatabaseManager(DatabaseManager):
    """Test database manager that creates clean database for each test."""

    def __init__(self):
        super().__init__()
        # Override settings for tests
        self._test_db_url = test_settings.database_url

    def connect(self) -> DatabaseConnection:
        """Create test database connection."""
        if self.connection is None:
            self.connection = DatabaseConnection(self._test_db_url)
            self._create_tables_if_needed()
        return self.connection

    def reset_database(self):
        """Reset database to clean state for tests."""
        if self.connection:
            self.connection.close()
            self.connection = None

        # Reconnect and recreate tables
        self.connect()


# Test database manager instance
test_db_manager = TestDatabaseManager()


@pytest.fixture
def db_connection() -> Generator[DatabaseConnection, None, None]:
    """Provide a clean database connection for each test."""
    # Reset database to clean state
    test_db_manager.reset_database()

    # Provide the connection
    connection = test_db_manager.connect()

    yield connection

    # Cleanup after test
    # Connection will be reset for next test


@pytest.fixture
def clean_database() -> Generator[DatabaseManager, None, None]:
    """Provide a clean database manager for each test."""
    # Reset database to clean state
    test_db_manager.reset_database()

    yield test_db_manager

    # Cleanup after test
    # Database will be reset for next test
