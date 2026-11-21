from pathlib import Path
from pydantic_settings import BaseSettings, SettingConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingConfigDict(env_prefix = "INSIGHTS")
    app_name: str = "Insights Hub Sales API"
    sales_csv_path: Path = REPO_ROOT / "data_pipeline" / "output" / "clean_sales.csv"

settings = Settings()
