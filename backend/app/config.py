from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py -> app/ -> backend/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INSIGHTS_")

    app_name: str = "Insights Hub Sales API"
    sales_csv_path: Path = REPO_ROOT / "data_pipeline" / "output" / "clean_sales.csv"


settings = Settings()
