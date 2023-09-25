from pydantic_settings import BaseSettings


class Config(BaseSettings):
    table_name: str = ""
    dynamodb_url: str | None = None
