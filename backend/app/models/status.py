from enum import Enum


class WSJFStatus(str, Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
