from uuid import UUID
from datetime import datetime

from app.core.database import db_manager
from app.models import (
    ProgramIncrement,
    ProgramIncrementCreate,
    ProgramIncrementResponse,
    ProgramIncrementUpdate,
    ProgramIncrementStats,
)


class ProgramIncrementService:
    def __init__(self):
        self.db = db_manager

    def create_pi(self, pi_data: ProgramIncrementCreate) -> ProgramIncrement:
        """Create a new Program Increment.

        Args:
            pi_data (ProgramIncrementCreate): The PI data to create.

        Returns:
            ProgramIncrement: The created PI with generated ID and timestamp.
        """
        pi = ProgramIncrement(**pi_data.model_dump())

        conn = self.db.connect()
        conn.execute(
            """
            INSERT INTO program_increments (
                id, name, description, start_date, end_date, status, created_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                str(pi.id),
                pi.name,
                pi.description,
                pi.start_date,
                pi.end_date,
                pi.status,
                pi.created_date,
            ],
        )

        return pi

    def get_pi(self, pi_id: UUID) -> ProgramIncrement | None:
        """Get a Program Increment by ID.

        Args:
            pi_id (UUID): The unique identifier of the PI.

        Returns:
            ProgramIncrement | None: The PI if found, None otherwise.
        """
        conn = self.db.connect()
        result = conn.execute(
            "SELECT * FROM program_increments WHERE id = ?", [str(pi_id)]
        ).fetchone()

        if not result:
            return None

        return self._row_to_pi(result)

    def get_pi_by_name(self, name: str) -> ProgramIncrement | None:
        """Get a Program Increment by name.

        Args:
            name (str): The name of the PI.

        Returns:
            ProgramIncrement | None: The PI if found, None otherwise.
        """
        conn = self.db.connect()
        result = conn.execute(
            "SELECT * FROM program_increments WHERE name = ?", [name]
        ).fetchone()

        if not result:
            return None

        return self._row_to_pi(result)

    def get_all_pis(self) -> list[ProgramIncrementResponse]:
        """Get all Program Increments with item counts.

        Returns:
            list[ProgramIncrementResponse]: List of PIs with item counts.
        """
        conn = self.db.connect()
        
        # Get PIs with item counts
        results = conn.execute(
            """
            SELECT p.*, COUNT(w.id) as item_count
            FROM program_increments p
            LEFT JOIN wsjf_items w ON p.id = w.program_increment_id
            GROUP BY p.id, p.name, p.description, p.start_date, p.end_date, p.status, p.created_date
            ORDER BY p.created_date DESC
            """
        ).fetchall()

        pis = []
        for row in results:
            pi = self._row_to_pi(row[:-1])  # Exclude item_count from PI data
            pi.item_count = row[-1]  # Set item_count from the last column
            pis.append(ProgramIncrementResponse(**pi.model_dump()))

        return pis

    def update_pi(self, pi_id: UUID, update_data: ProgramIncrementUpdate) -> ProgramIncrement | None:
        """Update a Program Increment.

        Args:
            pi_id (UUID): The unique identifier of the PI.
            update_data (ProgramIncrementUpdate): The data to update the PI with.

        Returns:
            ProgramIncrement | None: The updated PI if found, None otherwise.
        """
        existing_pi = self.get_pi(pi_id)
        if not existing_pi:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            return existing_pi

        # Build dynamic update query
        set_clauses = []
        values = []

        for field, value in update_dict.items():
            set_clauses.append(f"{field} = ?")
            values.append(value)

        values.append(str(pi_id))

        conn = self.db.connect()
        conn.execute(
            f"UPDATE program_increments SET {', '.join(set_clauses)} WHERE id = ?", values
        )

        return self.get_pi(pi_id)

    def delete_pi(self, pi_id: UUID) -> bool:
        """Delete a Program Increment and all associated WSJF items.

        Args:
            pi_id (UUID): The unique identifier of the PI to delete.

        Returns:
            bool: True if the PI was deleted, False if not found.
        """
        conn = self.db.connect()
        result = conn.execute("DELETE FROM program_increments WHERE id = ?", [str(pi_id)])
        return result.rowcount > 0

    def get_pi_stats(self, pi_id: UUID) -> ProgramIncrementStats | None:
        """Get statistics for a Program Increment.

        Args:
            pi_id (UUID): The unique identifier of the PI.

        Returns:
            ProgramIncrementStats | None: PI statistics if found, None otherwise.
        """
        pi = self.get_pi(pi_id)
        if not pi:
            return None

        conn = self.db.connect()
        
        # Get basic stats
        stats_result = conn.execute(
            """
            SELECT 
                COUNT(*) as total_items,
                AVG((business_value + time_criticality + risk_reduction) * 1.0 / job_size) as avg_wsjf_score
            FROM wsjf_items 
            WHERE program_increment_id = ?
            """,
            [str(pi_id)]
        ).fetchone()

        total_items = stats_result[0] if stats_result else 0
        avg_wsjf_score = round(stats_result[1], 2) if stats_result and stats_result[1] else 0.0

        # Get status distribution
        status_results = conn.execute(
            """
            SELECT status, COUNT(*) as count
            FROM wsjf_items 
            WHERE program_increment_id = ?
            GROUP BY status
            """,
            [str(pi_id)]
        ).fetchall()

        status_distribution = {row[0]: row[1] for row in status_results}

        # Get team distribution
        team_results = conn.execute(
            """
            SELECT COALESCE(team, 'Unassigned') as team, COUNT(*) as count
            FROM wsjf_items 
            WHERE program_increment_id = ?
            GROUP BY team
            """,
            [str(pi_id)]
        ).fetchall()

        team_distribution = {row[0]: row[1] for row in team_results}

        return ProgramIncrementStats(
            pi_id=pi_id,
            pi_name=pi.name,
            total_items=total_items,
            avg_wsjf_score=avg_wsjf_score,
            status_distribution=status_distribution,
            team_distribution=team_distribution,
        )

    def _row_to_pi(self, row) -> ProgramIncrement:
        """Convert database row to ProgramIncrement.

        Args:
            row: Database row tuple containing PI data.

        Returns:
            ProgramIncrement: Converted PI object.
        """
        # Handle UUID that might already be a UUID object or string
        pi_id = row[0] if isinstance(row[0], UUID) else UUID(row[0])

        return ProgramIncrement(
            id=pi_id,
            name=row[1],
            description=row[2],
            start_date=row[3],
            end_date=row[4],
            status=row[5],
            created_date=row[6],
            item_count=0,  # Will be set separately when needed
        )


# Global service instance
pi_service = ProgramIncrementService()