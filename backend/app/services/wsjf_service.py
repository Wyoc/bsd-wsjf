from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from app.core.database import db_manager
from app.models import (
    ProgramIncrement,
    WSJFItem,
    WSJFItemCreate,
    WSJFItemResponse,
    WSJFItemUpdate,
)


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
            ) VALUES (%(id)s, %(subject)s, %(description)s, %(business_value)s, %(time_criticality)s,
                     %(risk_reduction)s, %(job_size)s, %(status)s, %(owner)s, %(team)s, %(program_increment_id)s, %(created_date)s)
            """,
            {
                "id": str(item.id),
                "subject": item.subject,
                "description": item.description,
                "business_value": item.business_value.model_dump_json(),
                "time_criticality": item.time_criticality.model_dump_json(),
                "risk_reduction": item.risk_reduction.model_dump_json(),
                "job_size": item.job_size.model_dump_json(),
                "status": item.status.value,
                "owner": item.owner,
                "team": item.team,
                "program_increment_id": str(item.program_increment_id),
                "created_date": item.created_date,
            },
        )

        conn.commit()
        return item

    def get_item(self, item_id: UUID) -> WSJFItem | None:
        """Get a WSJF item by ID.

        Args:
            item_id (UUID): The unique identifier of the WSJF item.

        Returns:
            WSJFItem | None: The WSJF item if found, None otherwise.
        """
        conn = self.db.connect()

        result = conn.fetchone(
            "SELECT * FROM wsjf_items WHERE id = %(id)s", {"id": str(item_id)}
        )

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
            results = conn.fetchall(
                "SELECT * FROM wsjf_items WHERE program_increment_id = %(id)s ORDER BY created_date DESC",
                {"id": str(program_increment_id)},
            )
        else:
            results = conn.fetchall(
                "SELECT * FROM wsjf_items ORDER BY created_date DESC"
            )

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
        update_params = {
            field.split(" = ")[0]: values[i] for i, field in enumerate(set_clauses)
        }
        update_params["id"] = str(item_id)

        param_names = ", ".join(
            [
                f"{field.split(' = ')[0]} = %({field.split(' = ')[0]})s"
                for field in set_clauses
            ]
        )
        conn.execute(
            f"UPDATE wsjf_items SET {param_names} WHERE id = %(id)s", update_params
        )
        conn.commit()

        return self.get_item(item_id)

    def delete_item(self, item_id: UUID) -> bool:
        """Delete a WSJF item.

        Args:
            item_id (UUID): The unique identifier of the WSJF item to delete.

        Returns:
            bool: True if the item was deleted, False if not found.
        """
        conn = self.db.connect()
        conn.execute("DELETE FROM wsjf_items WHERE id = %(id)s", {"id": str(item_id)})
        conn.commit()
        return True

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
                ) VALUES (%(id)s, %(subject)s, %(description)s, %(business_value)s, %(time_criticality)s,
                         %(risk_reduction)s, %(job_size)s, %(status)s, %(owner)s, %(team)s, %(program_increment_id)s, %(created_date)s)
                """,
                {
                    "id": str(item.id),
                    "subject": item.subject,
                    "description": item.description,
                    "business_value": item.business_value.model_dump_json(),
                    "time_criticality": item.time_criticality.model_dump_json(),
                    "risk_reduction": item.risk_reduction.model_dump_json(),
                    "job_size": item.job_size.model_dump_json(),
                    "status": item.status.value,
                    "owner": item.owner,
                    "team": item.team,
                    "program_increment_id": str(item.program_increment_id),
                    "created_date": item.created_date,
                },
            )

        conn.commit()
        return items

    def get_sample_data(self) -> list[WSJFItemResponse]:
        """Generate sample WSJF data for demonstration.

        Returns:
            list[WSJFItemResponse]: List of sample WSJF items with priority rankings.
        """
        # Create or get sample PI
        conn = self.db.connect()

        # Check if sample PI exists
        pi_result = conn.fetchone(
            "SELECT id FROM program_increments WHERE name = %(name)s", {"name": "PI18"}
        )

        if pi_result:
            sample_pi_id = UUID(pi_result["id"])
        else:
            # Create sample PI
            sample_pi = ProgramIncrement(
                name="PI18",
                description="Sample Program Increment for demonstration",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=90),
                status="Planning",
            )

            conn.execute(
                """
                INSERT INTO program_increments (
                    id, name, description, start_date, end_date, status, created_date
                ) VALUES (%(id)s, %(name)s, %(description)s, %(start_date)s, %(end_date)s, %(status)s, %(created_date)s)
                """,
                {
                    "id": str(sample_pi.id),
                    "name": sample_pi.name,
                    "description": sample_pi.description,
                    "start_date": sample_pi.start_date,
                    "end_date": sample_pi.end_date,
                    "status": sample_pi.status,
                    "created_date": sample_pi.created_date,
                },
            )
            conn.commit()
            sample_pi_id = sample_pi.id

        from app.models.wsjf_item import JobSizeSubValues, WSJFSubValues

        sample_items = [
            WSJFItemCreate(
                subject="User Authentication System",
                description="Implement secure login and registration system",
                business_value=WSJFSubValues(
                    pms_business=21, dev_technical=13, ia_business=8
                ),
                time_criticality=WSJFSubValues(
                    consultants_business=13, support_business=5
                ),
                risk_reduction=WSJFSubValues(dev_business=8, devops_technical=3),
                job_size=JobSizeSubValues(dev=5, ia=3, devops=2, exploit=1),
                owner="Alice Johnson",
                team="Security Team",
                program_increment_id=sample_pi_id,
            ),
            WSJFItemCreate(
                subject="Mobile App Dashboard",
                description="Create responsive dashboard for mobile users",
                business_value=WSJFSubValues(pos_business=8, dev_business=5),
                time_criticality=WSJFSubValues(ia_technical=5, devops_business=3),
                risk_reduction=WSJFSubValues(
                    consultants_business=3, support_business=2
                ),
                job_size=JobSizeSubValues(dev=8, ia=5, devops=3, exploit=2),
                owner="Bob Smith",
                team="Mobile Team",
                program_increment_id=sample_pi_id,
            ),
            WSJFItemCreate(
                subject="Payment Gateway Integration",
                description="Integrate with third-party payment processors",
                business_value=WSJFSubValues(bos_agri_business=21, pms_business=13),
                time_criticality=WSJFSubValues(
                    bos_cabinet_business=13, consultants_business=8
                ),
                risk_reduction=WSJFSubValues(dev_technical=8, support_business=5),
                job_size=JobSizeSubValues(dev=8, ia=5, devops=3, exploit=1),
                owner="Carol Davis",
                team="Backend Team",
                program_increment_id=sample_pi_id,
            ),
        ]

        # Clear existing sample data and create new
        conn.execute(
            "DELETE FROM wsjf_items WHERE program_increment_id = %(id)s",
            {"id": str(sample_pi_id)},
        )
        conn.commit()

        created_items = self.create_batch(sample_items)
        return self._add_priorities(
            [WSJFItem.model_validate(item) for item in created_items]
        )

    def _row_to_wsjf_item(self, row: dict[str, Any]) -> WSJFItem:
        """Convert database row to WSJFItem.

        Args:
            row: Database row dictionary containing WSJF item data.

        Returns:
            WSJFItem: Converted WSJF item object.
        """
        import json

        from app.models.wsjf_item import JobSizeSubValues, WSJFSubValues

        # Handle UUID that might already be a UUID object or string
        item_id = row["id"] if isinstance(row["id"], UUID) else UUID(row["id"])

        # Parse JSON sub-values (PostgreSQL returns JSONB as dict, not string)
        business_value_data = (
            row["business_value"]
            if isinstance(row["business_value"], dict)
            else json.loads(row["business_value"])
        )
        time_criticality_data = (
            row["time_criticality"]
            if isinstance(row["time_criticality"], dict)
            else json.loads(row["time_criticality"])
        )
        risk_reduction_data = (
            row["risk_reduction"]
            if isinstance(row["risk_reduction"], dict)
            else json.loads(row["risk_reduction"])
        )
        job_size_data = (
            row["job_size"]
            if isinstance(row["job_size"], dict)
            else json.loads(row["job_size"])
        )

        business_value = WSJFSubValues.model_validate(business_value_data)
        time_criticality = WSJFSubValues.model_validate(time_criticality_data)
        risk_reduction = WSJFSubValues.model_validate(risk_reduction_data)
        job_size = JobSizeSubValues.model_validate(job_size_data)

        # Handle program_increment_id UUID
        pi_id = (
            row["program_increment_id"]
            if isinstance(row["program_increment_id"], UUID)
            else UUID(row["program_increment_id"])
        )

        return WSJFItem(
            id=item_id,
            subject=row["subject"],
            description=row["description"],
            business_value=business_value,
            time_criticality=time_criticality,
            risk_reduction=risk_reduction,
            job_size=job_size,
            status=row["status"],
            owner=row["owner"],
            team=row["team"],
            program_increment_id=pi_id,
            created_date=row["created_date"],
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
