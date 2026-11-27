from app.config import Settings
from app.repositories.protocol import SalesRepositoryProtocol
from app.repositories.sales_repository import SalesRepository


def build_sales_repository(settings: Settings) -> SalesRepositoryProtocol:
    """Pick the repository from the REPOSITORY setting: "file" or "postgres"."""
    if settings.repository == "postgres":
        # Imported here so file mode never needs a database connection.
        from app.db.session import engine
        from app.repositories.postgres_sales_repository import PostgresSalesRepository

        return PostgresSalesRepository(engine)

    return SalesRepository(settings.sales_csv_path)
