"""Shared test configuration and fixtures."""

import asyncio
import os

import pytest

# Set test environment variables before importing app modules
os.environ["POSTGRES_DB"] = "wsjf_test"
os.environ["EXCEL_EXPORT_PATH"] = "./test_exports/"

from app.core.test_database import test_db_manager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment for each test."""
    # Ensure test export directory exists
    os.makedirs("./test_exports/", exist_ok=True)

    yield

    # Cleanup after test
    # Clean up any test files if needed


@pytest.fixture
def clean_db():
    """Provide a clean database for each test."""
    test_db_manager.reset_database()
    yield test_db_manager
    # Database will be reset for next test


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "database: mark test as requiring database connection"
    )
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add default markers."""
    for item in items:
        # Add database marker to tests that use database fixtures
        if any(
            fixture in item.fixturenames
            for fixture in ["db_connection", "clean_database", "api_client_with_db"]
        ):
            item.add_marker(pytest.mark.database)

        # Add integration marker to API tests
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # Add unit marker to service and model tests
        if any(
            name in item.nodeid
            for name in [
                "test_wsjf_service",
                "test_pi_service",
                "test_database_factory",
            ]
        ):
            item.add_marker(pytest.mark.unit)
