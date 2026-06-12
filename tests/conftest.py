"""Fixtures de test — base PostgreSQL réelle, isolée entre les tests.

Infra fournie : le candidat n'écrit pas de plomberie de test.
La base de test (`<SQL_DATABASE>_test`) est créée à la volée si besoin.
Le schéma est bootstrappé via `Base.metadata` (rapide) ; la migration
Alembic reste le livrable de production (T1).
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import server.etl.models  # noqa: F401  (enregistre les tables sur Base)
from server.config import config
from server.database import Base

TEST_DB = f"{config.SQL_DATABASE}_test"
TEST_URL = (
    f"postgresql+psycopg2://{config.SQL_USER}:{config.SQL_PASSWORD}@"
    f"{config.SQL_HOST}:{config.SQL_PORT}/{TEST_DB}"
)


def _ensure_test_database() -> None:
    """Crée la base de test si elle n'existe pas."""
    admin = create_engine(
        f"postgresql+psycopg2://{config.SQL_USER}:{config.SQL_PASSWORD}@"
        f"{config.SQL_HOST}:{config.SQL_PORT}/postgres",
        isolation_level="AUTOCOMMIT",
    )
    with admin.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"),
            {"n": TEST_DB},
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB}"'))
    admin.dispose()


@pytest.fixture(scope="session")
def engine():
    """Moteur sur la base de test, schéma créé via metadata."""
    _ensure_test_database()
    eng = create_engine(TEST_URL, future=True)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture()
def db_session(engine):
    """Session de test ; les tables sont vidées après chaque test."""
    session_factory = sessionmaker(bind=engine, future=True)
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                conn.execute(
                    text(f'TRUNCATE TABLE "{table.name}" CASCADE')
                )
