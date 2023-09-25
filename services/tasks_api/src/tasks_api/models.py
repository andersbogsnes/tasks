from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID


class TaskStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass
class Task:
    id: UUID
    title: str
    status: TaskStatus
    owner: str

    @classmethod
    def create(cls, task_id: UUID, title: str, owner: str) -> Self:
        return cls(task_id, title, TaskStatus.OPEN, owner)

    def close(self):
        self.status = TaskStatus.CLOSED
