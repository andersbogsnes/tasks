import uuid

import boto3
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from moto import mock_dynamodb
from mypy_boto3_dynamodb import DynamoDBClient

from tasks_api import app
from tasks_api.models import Task, TaskStatus
from tasks_api.store import TaskStore


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def dynamodb_table() -> str:
    with mock_dynamodb():
        client: DynamoDBClient = boto3.client("dynamodb")
        table_name = "test-table"
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GS1PK", "AttributeType": "S"},
                {"AttributeName": "GS1SK", "AttributeType": "S"},
            ],
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GS1",
                    "KeySchema": [
                        {"AttributeName": "GS1PK", "KeyType": "HASH"},
                        {"AttributeName": "GS1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        )
        yield table_name


def test_added_task_retrieved_by_id(dynamodb_table: str):
    repository = TaskStore(table_name=dynamodb_table)
    task = Task.create(uuid.uuid4(), "Clean your office", "john@doe.com")

    repository.add(task)

    assert repository.get_by_id(task_id=str(task.id), owner=task.owner) == task


def test_healthcheck(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "OK"}


def test_open_tasks_listed(dynamodb_table: str):
    repository = TaskStore(table_name=dynamodb_table)
    open_task = Task.create(uuid.uuid4(), "Clean your office", "john@doe.com")
    closed_task = Task(
        uuid.uuid4(), "Clean you office", TaskStatus.CLOSED, "john@doe.com"
    )

    repository.add(open_task)
    repository.add(closed_task)

    assert repository.list_open(owner=open_task.owner) == [open_task]


def test_closed_tasks_listed(dynamodb_table: str):
    repository = TaskStore(table_name=dynamodb_table)
    open_task = Task.create(uuid.uuid4(), "Clean your office", "john@doe.com")
    closed_task = Task(
        uuid.uuid4(),
        title="Clean your office",
        status=TaskStatus.CLOSED,
        owner="john@doe.com",
    )
    repository.add(open_task)
    repository.add(closed_task)

    assert repository.list_closed(owner=open_task.owner) == [closed_task]
