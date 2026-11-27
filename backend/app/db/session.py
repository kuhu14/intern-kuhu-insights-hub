from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# One engine (connection pool) for the whole process. Creating it does not connect;
# the first query does.
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine)
