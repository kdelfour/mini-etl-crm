"""Moteur SQLAlchemy, session et base déclarative.

Calqué sur `server/common/sql/data.py` du monolith : `declarative_base`
+ un `BaseModel` abstrait portant les colonnes d'audit communes
(`id`, `created_at`, `updated_at`).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker

from server.config import config

engine = create_engine(config.url, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)

Base = declarative_base(name="Base")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class BaseModel:
    """Colonnes d'audit communes (mixin, comme dans le monolith).

    ⚠️ `updated_at` ici = date de mise à jour de la LIGNE (audit interne).
    À ne PAS confondre avec l'`updated_at` qui provient de l'export CRM
    (l'horodatage source, utile pour départager les versions d'un compte).
    """

    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )
