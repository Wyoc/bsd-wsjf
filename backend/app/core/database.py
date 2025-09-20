import duckdb

from .config import settings


class DatabaseManager:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.DATABASE_URL
        self.connection: duckdb.DuckDBPyConnection | None = None

    def connect(self) -> duckdb.DuckDBPyConnection:
        """Create or get database connection.

        Returns:
            duckdb.DuckDBPyConnection: Active database connection.
        """
        if self.connection is None:
            self.connection = duckdb.connect(self.db_path)
            self._create_tables_if_needed(self.connection)
        return self.connection

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def _create_tables_if_needed(self, connection: duckdb.DuckDBPyConnection):
        """Create database tables if they don't exist."""
        # Drop tables to ensure we have the updated schema
        drop_tables_sql = [
            "DROP TABLE IF EXISTS wsjf_items;",
            "DROP TABLE IF EXISTS program_increments;"
        ]
        
        for sql in drop_tables_sql:
            connection.execute(sql)
        
        # Create program_increments table
        create_pi_table_sql = """
        CREATE TABLE program_increments (
            id UUID PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            description VARCHAR(500) DEFAULT '',
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Planning',
            created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CHECK (end_date > start_date),
            CHECK (status IN ('Planning', 'Active', 'Completed', 'Cancelled'))
        );
        """
        
        # Create wsjf_items table with foreign key to program_increments
        create_wsjf_table_sql = """
        CREATE TABLE wsjf_items (
            id UUID PRIMARY KEY,
            subject VARCHAR(200) NOT NULL,
            description VARCHAR(1000) DEFAULT '',
            business_value INTEGER NOT NULL CHECK (business_value IN (1, 2, 3, 5, 8, 13, 21)),
            time_criticality INTEGER NOT NULL CHECK (time_criticality IN (1, 2, 3, 5, 8, 13, 21)),
            risk_reduction INTEGER NOT NULL CHECK (risk_reduction IN (1, 2, 3, 5, 8, 13, 21)),
            job_size INTEGER NOT NULL CHECK (job_size IN (1, 2, 3, 5, 8, 13, 21)),
            status VARCHAR(20) NOT NULL DEFAULT 'New',
            owner VARCHAR(100),
            team VARCHAR(100),
            program_increment_id UUID NOT NULL,
            created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (program_increment_id) REFERENCES program_increments(id)
        );
        """

        connection.execute(create_pi_table_sql)
        connection.execute(create_wsjf_table_sql)

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Keep connection open for reuse
        pass


# Global database manager instance
db_manager = DatabaseManager()
