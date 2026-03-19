import os
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./picasyfijas.db")

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    from app.db_models import GameRecord

    max_retries = int(os.getenv("DB_INIT_MAX_RETRIES", "15"))
    retry_delay_seconds = float(os.getenv("DB_INIT_RETRY_DELAY", "2"))

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError as exc:
            last_error = exc
            if attempt == max_retries:
                break
            time.sleep(retry_delay_seconds)

    if last_error is not None:
        raise last_error
