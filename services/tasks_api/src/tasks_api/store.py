from dataclasses import dataclass
from uuid import UUID

import boto3
from mypy_boto3_dynamodb import DynamoDBClient

from tasks_api.models import Task, TaskStatus


@dataclass
class TaskStore:
    table_name: str

    @property
    def dynamodb(self):
        return boto3.resource("dynamodb")

    def add(self, task: Task) -> None:

        table = self.dynamodb.Table(self.table_name)
        table.put_item(
            Item={
                "PK": f"#{task.owner}",
                "SK": f"#{task.id}",
                "id": str(task.id),
                "title": task.title,
                "status": task.status.value,
                "owner": task.owner
            }
        )

    def get_by_id(self, task_id: str, owner: str) -> Task:
        table = self.dynamodb.Table(self.table_name)
        record = table.get_item(Key={"PK": f"#{owner}", "SK": f"#{task_id}"})

        return Task(id=UUID(record["Item"]["id"]),
                    title=record["Item"]['title'],
                    owner=record["Item"]["owner"],
                    status=TaskStatus[record["Item"]["status"]]
                    )
