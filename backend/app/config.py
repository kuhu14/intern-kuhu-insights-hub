from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

# config.py -> app/ -> backend/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INSIGHTS_",
        env_file=REPO_ROOT / ".env",  # read if present; a missing file is fine
        extra="ignore",  # .env may hold variables this class does not use
    )

    app_name: str = "Insights Hub Sales API"
    sales_csv_path: Path = REPO_ROOT / "data_pipeline" / "output" / "clean_sales.csv"
    # Only the local frontend may call this API from a browser.
    cors_origins: list[str] = ["http://localhost:3000"]

    # Where sales data comes from: "file" (the Week 2 CSV) or "postgres".
    repository: Literal["file", "postgres"] = Field(
        "file", validation_alias="REPOSITORY"
    )

    # Postgres connection: the same POSTGRES_* names that docker-compose.yml uses.
    postgres_user: str = Field("insights", validation_alias="POSTGRES_USER")
    postgres_password: str = Field("", validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field("insights_hub", validation_alias="POSTGRES_DB")
    postgres_host: str = Field("localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, validation_alias="POSTGRES_PORT")

    @property
    def database_url(self) -> URL:
        # URL.create safely escapes special characters such as "@" in the password.
        return URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


settings = Settings()
