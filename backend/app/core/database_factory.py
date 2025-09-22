"""PostgreSQL database connection factory."""

from typing import Any

import psycopg
from psycopg.rows import dict_row

from .config import settings


class DatabaseConnection:
    """PostgreSQL database connection wrapper."""

    def __init__(self, connection_url: str):
        self.connection = psycopg.connect(connection_url, row_factory=dict_row)
        self.connection.autocommit = False

    def execute(self, query: str, params: dict[str, Any] | None = None) -> None:
        """Execute a query without returning results."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)

    def fetchall(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a query and return all results as dictionaries."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetchone(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Execute a query and return the first result as a dictionary."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.connection.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.connection.rollback()


class DatabaseManager:
    """Database manager for PostgreSQL."""

    def __init__(self):
        self.connection: DatabaseConnection | None = None

    def connect(self) -> DatabaseConnection:
        """Create or get database connection."""
        if self.connection is None:
            self.connection = DatabaseConnection(settings.database_url)
            self._create_tables_if_needed()

        return self.connection

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def _create_tables_if_needed(self):
        """Create database tables if they don't exist."""
        connection = self.connection
        if not connection:
            return

        # Drop tables to ensure we have the updated schema
        drop_tables_sql = [
            "DROP TABLE IF EXISTS wsjf_items CASCADE;",
            "DROP TABLE IF EXISTS program_increments CASCADE;",
        ]

        for sql in drop_tables_sql:
            connection.execute(sql)

        # Create program_increments table
        create_pi_table_sql = """
        CREATE TABLE program_increments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL UNIQUE,
            description VARCHAR(500) DEFAULT '',
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Planning',
            created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT check_end_date CHECK (end_date > start_date),
            CONSTRAINT check_status CHECK (status IN ('Planning', 'Active', 'Completed', 'Cancelled'))
        );
        """

        # Create wsjf_items table with foreign key to program_increments
        create_wsjf_table_sql = """
        CREATE TABLE wsjf_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            subject VARCHAR(200) NOT NULL,
            description VARCHAR(1000) DEFAULT '',
            business_value JSONB NOT NULL,
            time_criticality JSONB NOT NULL,
            risk_reduction JSONB NOT NULL,
            job_size JSONB NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'New',
            owner VARCHAR(100),
            team VARCHAR(100),
            program_increment_id UUID NOT NULL,
            created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (program_increment_id) REFERENCES program_increments(id) ON DELETE CASCADE
        );
        """

        connection.execute(create_pi_table_sql)
        connection.execute(create_wsjf_table_sql)
        connection.commit()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Keep connection open for reuse
        pass


# Global database manager instance
db_manager = DatabaseManager()
