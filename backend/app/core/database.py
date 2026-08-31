from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


# ============================================================
# DATABASE ENGINE
# ============================================================

database_url = settings.database_url

# SQLite requires this option when the application can access
# the database from multiple threads (common with FastAPI).
connect_args = {}

if database_url.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }


engine = create_engine(
    database_url,
    connect_args=connect_args,
)


# ============================================================
# DATABASE SESSION
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ============================================================
# BASE MODEL
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()