from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context
from app.config import settings
from app.db import models  # noqa: F401  (importing registers the tables on Base)
from app.db.base import Base

# The Alembic Config object, which gives access to values in alembic.ini.
config = context.config

# Set up Python logging from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Our models' tables, used by "alembic revision --autogenerate".
target_metadata = Base.metadata

# The database URL comes from .env via app.config, never from alembic.ini,
# so the password is not stored in a committed file.
DATABASE_URL = settings.database_url


def run_migrations_offline() -> None:
    """Write the migration SQL to the screen instead of running it (--sql)."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the database and run the migrations."""
    engine = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
