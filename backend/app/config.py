from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://grantfunnel:grantfunnel@localhost:5432/grantfunnel"
    database_url_sync: str = "postgresql://grantfunnel:grantfunnel@localhost:5432/grantfunnel"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
