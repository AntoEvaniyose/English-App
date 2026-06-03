# FastAPI English App

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run server

```bash
uvicorn app.main:app --reload
```

## Run tests

```bash
pytest
```


📦 Alembic Setup (Database Migrations)

This project uses Alembic for managing database schema migrations.

🔧 1. Install Dependencies
pip install alembic pydantic-settings
🚀 2. Initialize Alembic
alembic init alembic

This creates:

alembic/ directory
alembic.ini configuration file
⚙️ 3. Configure Database URL

Update alembic/env.py:

from app.core.config import settings

db_url = settings.DATABASE_URL.replace("%", "%%")
config.set_main_option(
    "sqlalchemy.url",
    db_url,
)
🧠 4. Register Models

Make sure all models are imported so Alembic can detect them.

In alembic/env.py:

from app.db.base import Base
from app.db import models  # loads all models
<!-- # app/db/models/__init__.py

from app.db.models.user import User,UserRefreshToken
from app.db.models.admin import Admin,AdminRefreshToken -->

target_metadata = Base.metadata

⚠️ Without this, migrations will not detect your tables.

🧬 5. Remove create_all

If you are using Alembic, do not use:

Base.metadata.create_all(bind=engine)
📝 6. Create Migration
alembic revision --autogenerate -m "Initial migration"
⬆️ 7. Apply Migration
alembic upgrade head
🔄 8. Future Changes

Whenever models are updated:

alembic revision --autogenerate -m "Describe changes"
alembic upgrade head
🧪 9. Verify

Check generated migrations inside:

alembic/versions/