"""Schémas pydantic de l'API d'import (boilerplate fourni).

NB : la validation au niveau **enregistrement** (comptes, interactions,
pièges `last_name: null` / `updated_at: "bad-date"`) fait partie de la
tâche T2 — à écrire dans `pipeline.py`.
"""

from __future__ import annotations

from pydantic import BaseModel


class ImportRequest(BaseModel):
    """Corps de `POST /imports`."""

    tenant: str
    file: str  # chemin de l'export CRM à ingérer


class ImportRunResponse(BaseModel):
    """État d'un run d'import renvoyé par l'API."""

    id: str
    tenant: str
    status: str
    created: int = 0
    updated: int = 0
    skipped: int = 0
    rejected: int = 0
