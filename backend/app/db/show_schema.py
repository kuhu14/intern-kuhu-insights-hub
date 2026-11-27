"""Print the CREATE TABLE SQL the models produce. Run from backend/:

    python -m app.db.show_schema

Nothing is written to the database.
"""

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app.db import models  # noqa: F401  (importing registers the tables on Base)
from app.db.base import Base


def main() -> None:
    for table in Base.metadata.sorted_tables:
        ddl = CreateTable(table).compile(dialect=postgresql.dialect())
        print(str(ddl).strip() + ";\n")
    print(f"{len(Base.metadata.tables)} tables")


if __name__ == "__main__":
    main()
