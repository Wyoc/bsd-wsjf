from enum import Enum


class WSJFStatus(str, Enum):
    NEW = "New"
    GO = "Go"
    NO_GO = "No Go"


class GoNoGoStatus(str, Enum):
    PENDING = "Pending"
    GO = "Go"
    NO_GO = "No Go"
