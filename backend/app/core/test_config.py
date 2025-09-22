"""Test configuration for WSJF backend."""

from app.core.config import Settings


class TestSettings(Settings):
    """Test-specific settings that override default configuration."""

    # Use test database
    POSTGRES_DB: str = "wsjf_test"

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL for tests."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


# Test settings instance
test_settings = TestSettings()
