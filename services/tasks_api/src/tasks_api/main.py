import uuid
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, Header, status
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from tasks_api.config import Config
from tasks_api.models import Task
from tasks_api.schemas import APITask, APITaskList, CloseTask, CreateTask
from tasks_api.store import TaskStore

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = Config()


def get_task_store() -> TaskStore:
    return TaskStore(config.table_name, dynamodb_url=config.dynamodb_url)


def get_user_email(authorization: str | None = Header(default=None)) -> str:
    return jwt.decode(authorization, options={"verify_signature": False})[
        "cognito:username"
    ]


@app.get("/api/health")
def health():
    return {"message": "OK"}


@app.post(
    "/api/create-task", response_model=APITask, status_code=status.HTTP_201_CREATED
)
def create_task(
    parameters: CreateTask,
    user_email: Annotated[str, Depends(get_user_email)],
    task_store: Annotated[TaskStore, Depends(get_task_store)],
):
    task = Task.create(task_id=uuid.uuid4(), title=parameters.title, owner=user_email)
    task_store.add(task)

    return task


@app.get("/api/open-tasks", response_model=APITaskList)
def open_tasks(
    user_email: Annotated[str, Depends(get_user_email)],
    task_store: Annotated[TaskStore, Depends(get_task_store)],
):
    return APITaskList(results=task_store.list_open(user_email))


@app.post("/api/close-task", response_model=APITask)
def close_task(
    parameters: CloseTask,
    user_email: Annotated[str, Depends(get_user_email)],
    task_store: Annotated[TaskStore, Depends(get_task_store)],
):
    task = task_store.get_by_id(parameters.id, owner=user_email)
    task.close()
    task_store.add(task)
    return task


@app.get("/api/closed-tasks", response_model=APITaskList)
def closed_tasks(
    user_email: Annotated[str, Depends(get_user_email)],
    task_store: Annotated[TaskStore, Depends(get_task_store)],
):
    return APITaskList(results=task_store.list_closed(owner=user_email))


handle = Mangum(app)
