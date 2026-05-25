from enum import Enum
from typing import Dict, List, Optional, Set


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


VALID_TRANSITIONS: Dict[str, Set[str]] = {
    TaskStatus.PENDING: {TaskStatus.PROCESSING, TaskStatus.CANCELLED},
    TaskStatus.PROCESSING: {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.FAILED: {TaskStatus.PENDING},
    TaskStatus.CANCELLED: set(),
    TaskStatus.COMPLETED: set(),
}


def can_transition(current: str, target: str) -> bool:
    allowed = VALID_TRANSITIONS.get(current, set())
    return target in allowed


def validate_transition(current: str, target: str) -> None:
    if not can_transition(current, target):
        raise ValueError(f"Invalid status transition: {current} -> {target}")


def check_dependencies_met(depends_on: List[str], task_statuses: Dict[str, str]) -> bool:
    if not depends_on:
        return True
    for dep_id in depends_on:
        status = task_statuses.get(str(dep_id))
        if status != TaskStatus.COMPLETED:
            return False
    return True


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


PRIORITY_ORDER = {
    TaskPriority.LOW: 0,
    TaskPriority.NORMAL: 1,
    TaskPriority.HIGH: 2,
    TaskPriority.URGENT: 3,
}


DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAYS = [60, 300, 900]


def get_retry_delay(attempt: int, base_delays: Optional[list] = None) -> int:
    delays = base_delays or DEFAULT_RETRY_DELAYS
    if attempt - 1 < len(delays):
        return delays[attempt - 1]
    return delays[-1] * (2 ** (attempt - len(delays)))
