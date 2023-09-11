import uuid

import boto3
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from moto import mock_dynamodb

from tasks_api import app
from tasks_api.models import Task
from tasks_api.store import TaskStore


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture()
def dynamodb_table() -> str:
    with mock_dynamodb():
        client = boto3.client("dynamodb")
        table_name = "test-table"
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",
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
