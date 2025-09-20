from uuid import UUID
from datetime import datetime, timedelta

from app.core.database import db_manager
from app.models import WSJFItem, WSJFItemCreate, WSJFItemResponse, WSJFItemUpdate
from app.models import ProgramIncrement, ProgramIncrementCreate


class WSJFService:
    def __init__(self):
        self.db = db_manager

    def create_item(self, item_data: WSJFItemCreate) -> WSJFItem:
        """Create a new WSJF item.

        Args:
            item_data (WSJFItemCreate): The WSJF item data to create.

        Returns:
            WSJFItem: The created WSJF item with generated ID and timestamp.
        """
        item = WSJFItem(**item_data.model_dump())

        conn = self.db.connect()
        conn.execute(
            """
            INSERT INTO wsjf_items (
                id, subject, description, business_value, time_criticality,
                risk_reduction, job_size, status, owner, team, program_increment_id, created_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                str(item.id),
                item.subject,
                item.description,
                item.business_value,
                item.time_criticality,
                item.risk_reduction,
                item.job_size,
                item.status.value,
                item.owner,
                item.team,
                str(item.program_increment_id),
                item.created_date,
            ],
        )

        return item

    def get_item(self, item_id: UUID) -> WSJFItem | None:
        """Get a WSJF item by ID.

        Args:
            item_id (UUID): The unique identifier of the WSJF item.

        Returns:
            WSJFItem | None: The WSJF item if found, None otherwise.
        """
        conn = self.db.connect()
        result = conn.execute(
            "SELECT * FROM wsjf_items WHERE id = ?", [str(item_id)]
        ).fetchone()

        if not result:
            return None

        return self._row_to_wsjf_item(result)

    def get_all_items(
        self, program_increment_id: UUID | None = None
    ) -> list[WSJFItemResponse]:
        """Get all WSJF items, optionally filtered by Program Increment ID.

        Args:
            program_increment_id (UUID | None, optional): Filter by Program Increment ID.
                Defaults to None (returns all items).

        Returns:
            list[WSJFItemResponse]: List of WSJF items with priority rankings.
        """
        conn = self.db.connect()
        if program_increment_id:
            results = conn.execute(
                "SELECT * FROM wsjf_items WHERE program_increment_id = ? ORDER BY created_date DESC",
                [str(program_increment_id)],
            ).fetchall()
        else:
            results = conn.execute(
                "SELECT * FROM wsjf_items ORDER BY created_date DESC"
            ).fetchall()

        items = [self._row_to_wsjf_item(row) for row in results]
        return self._add_priorities(items)

    def update_item(
        self, item_id: UUID, update_data: WSJFItemUpdate
    ) -> WSJFItem | None:
        """Update a WSJF item.

        Args:
            item_id (UUID): The unique identifier of the WSJF item.
            update_data (WSJFItemUpdate): The data to update the item with.

        Returns:
            WSJFItem | None: The updated WSJF item if found, None otherwise.
        """
        existing_item = self.get_item(item_id)
        if not existing_item:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            return existing_item

        # Build dynamic update query
        set_clauses = []
        values = []

        for field, value in update_dict.items():
            if field == "status" and value is not None:
                set_clauses.append(f"{field} = ?")
                values.append(value.value)
            else:
                set_clauses.append(f"{field} = ?")
                values.append(value)

        values.append(str(item_id))

        conn = self.db.connect()
        conn.execute(
            f"UPDATE wsjf_items SET {', '.join(set_clauses)} WHERE id = ?", values
        )

        return self.get_item(item_id)

    def delete_item(self, item_id: UUID) -> bool:
        """Delete a WSJF item.

        Args:
            item_id (UUID): The unique identifier of the WSJF item to delete.

        Returns:
            bool: True if the item was deleted, False if not found.
        """
        conn = self.db.connect()
        result = conn.execute("DELETE FROM wsjf_items WHERE id = ?", [str(item_id)])
        return result.rowcount > 0

    def create_batch(self, items_data: list[WSJFItemCreate]) -> list[WSJFItem]:
        """Create multiple WSJF items in batch.

        Args:
            items_data (list[WSJFItemCreate]): List of WSJF item data to create.

        Returns:
            list[WSJFItem]: List of created WSJF items.
        """
        items = []

        conn = self.db.connect()
        for item_data in items_data:
            item = WSJFItem(**item_data.model_dump())
            items.append(item)

            conn.execute(
                """
                INSERT INTO wsjf_items (
                    id, subject, description, business_value, time_criticality,
                    risk_reduction, job_size, status, owner, team, program_increment_id, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    str(item.id),
                    item.subject,
                    item.description,
                    item.business_value,
                    item.time_criticality,
                    item.risk_reduction,
                    item.job_size,
                    item.status.value,
                    item.owner,
                    item.team,
                    str(item.program_increment_id),
                    item.created_date,
                ],
            )

        return items

    def get_sample_data(self) -> list[WSJFItemResponse]:
        """Generate sample WSJF data for demonstration.

        Returns:
            list[WSJFItemResponse]: List of sample WSJF items with priority rankings.
        """
        # Create or get sample PI
        conn = self.db.connect()
        
        # Check if sample PI exists
        pi_result = conn.execute(
            "SELECT id FROM program_increments WHERE name = 'PI18'"
        ).fetchone()
        
        if pi_result:
            sample_pi_id = UUID(pi_result[0])
        else:
            # Create sample PI
            sample_pi = ProgramIncrement(
                name="PI18",
                description="Sample Program Increment for demonstration",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=90),
                status="Planning"
            )
            
            conn.execute(
                """
                INSERT INTO program_increments (
                    id, name, description, start_date, end_date, status, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    str(sample_pi.id),
                    sample_pi.name,
                    sample_pi.description,
                    sample_pi.start_date,
                    sample_pi.end_date,
                    sample_pi.status,
                    sample_pi.created_date,
                ],
            )
            sample_pi_id = sample_pi.id

        sample_items = [
            WSJFItemCreate(
                subject="User Authentication System",
                description="Implement secure login and registration system",
                business_value=8,
                time_criticality=8,
                risk_reduction=5,
                job_size=5,
                owner="Alice Johnson",
                team="Security Team",
                program_increment_id=sample_pi_id,
            ),
            WSJFItemCreate(
                subject="Mobile App Dashboard",
                description="Create responsive dashboard for mobile users",
                business_value=5,
                time_criticality=3,
                risk_reduction=3,
                job_size=8,
                owner="Bob Smith",
                team="Mobile Team",
                program_increment_id=sample_pi_id,
            ),
            WSJFItemCreate(
                subject="Payment Gateway Integration",
                description="Integrate with third-party payment processors",
                business_value=13,
                time_criticality=8,
                risk_reduction=5,
                job_size=8,
                owner="Carol Davis",
                team="Backend Team",
                program_increment_id=sample_pi_id,
            ),
        ]

        # Clear existing sample data and create new
        conn.execute("DELETE FROM wsjf_items WHERE program_increment_id = ?", [str(sample_pi_id)])

        created_items = self.create_batch(sample_items)
        return self._add_priorities(
            [WSJFItem.model_validate(item) for item in created_items]
        )

    def _row_to_wsjf_item(self, row) -> WSJFItem:
        """Convert database row to WSJFItem.

        Args:
            row: Database row tuple containing WSJF item data.

        Returns:
            WSJFItem: Converted WSJF item object.
        """
        # Handle UUID that might already be a UUID object or string
        item_id = row[0] if isinstance(row[0], UUID) else UUID(row[0])

        # Handle program_increment_id UUID
        pi_id = row[10] if isinstance(row[10], UUID) else UUID(row[10])
        
        return WSJFItem(
            id=item_id,
            subject=row[1],
            description=row[2],
            business_value=row[3],
            time_criticality=row[4],
            risk_reduction=row[5],
            job_size=row[6],
            status=row[7],
            owner=row[8],
            team=row[9],
            program_increment_id=pi_id,
            created_date=row[11],
        )

    def _add_priorities(self, items: list[WSJFItem]) -> list[WSJFItemResponse]:
        """Add priority rankings based on WSJF scores.

        Args:
            items (list[WSJFItem]): List of WSJF items to rank.

        Returns:
            list[WSJFItemResponse]: List of WSJF items with priority rankings.
        """
        # Sort by WSJF score descending
        sorted_items = sorted(items, key=lambda x: x.wsjf_score, reverse=True)

        response_items = []
        for i, item in enumerate(sorted_items):
            response_item = WSJFItemResponse(**item.model_dump(), priority=i + 1)
            response_items.append(response_item)

        return response_items


# Global service instance
wsjf_service = WSJFService()