from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://tasktracker:tasktracker@localhost:5432/tasktracker"
    cors_origins: str = "http://localhost:5173"
    attachments_dir: str = "./data/attachments"
    gcp_project_id: str = ""
    gcs_bucket: str = ""
    pubsub_topic: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
