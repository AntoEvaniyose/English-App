from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True,  pool_recycle=300,
    pool_size=5,
    max_overflow=0)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import redis
from app.core.config import settings
 
redis_client = redis.Redis.from_url(
    settings.CELERY_RESULT_BACKEND,
    decode_responses=True
)        