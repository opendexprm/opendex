# Path: radicale/storage-postgresql/radicale_storage_postgresql/migrations/env.py
"""Alembic environment for the Radicale PostgreSQL storage plugin.

Supports two execution modes:
  1. CLI       — `cd radicale/storage-postgresql && alembic upgrade head`
                 reads sqlalchemy.url from alembic.ini (or RADICALE_DB_URL env var)
  2. Plugin    — called programmatically from Storage.__init__() at Radicale startup;
                 the engine is passed via config.attributes["connection"]
"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

import importlib.util
import sys
from pathlib import Path

# Load db.py directly — avoids importing __init__.py which depends on radicale
# (radicale is only available inside the Docker container, not in the local dev venv).
_db_path = Path(__file__).resolve().parent.parent / "db.py"
_spec = importlib.util.spec_from_file_location("radicale_storage_postgresql.db", _db_path)
_db = importlib.util.module_from_spec(_spec)
sys.modules["radicale_storage_postgresql.db"] = _db
_spec.loader.exec_module(_db)
Base = _db.Base

# -- Alembic Config object ---------------------------------------------------
config = context.config

# Interpret the config file for Python logging (only when run from CLI)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    """Resolve the database URL — env var takes precedence over alembic.ini."""
    return os.environ.get(
        "RADICALE_DB_URL",
        config.get_main_option("sqlalchemy.url", ""),
    )


def run_migrations_offline() -> None:
    """Generate SQL script without a live database connection."""
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database."""
    # When called from the plugin, the engine is pre-supplied.
    connectable = config.attributes.get("connection")
    if connectable is None:
        connectable = create_engine(_get_url())

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
