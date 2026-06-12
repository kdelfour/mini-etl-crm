"""Environnement Alembic — calqué sur `migrations/env.py` du monolith.

Lit l'URL depuis `server.config`, cible `Base.metadata`, et importe les
modèles pour qu'ils soient enregistrés avant l'autogénération.
"""

import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.append(".")

import server.etl.models  # noqa: E402,F401  (enregistre les tables)
from server.config import config as db_config  # noqa: E402
from server.database import Base  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online() -> None:
    """Migrations en mode 'online'."""
    config.set_main_option("sqlalchemy.url", db_config.url)
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=db_config.url,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


def run_migrations_offline() -> None:
    """Migrations en mode 'offline'."""
    context.configure(
        url=db_config.url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
