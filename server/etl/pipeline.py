"""Pipeline ETL — TÂCHES T2 à T4 (cœur de l'exercice).

Les fonctions reçoivent une `Session` SQLAlchemy en paramètre
(injectable depuis les tests et depuis la tâche Celery) — c'est un
choix de conception volontaire pour la testabilité.

Le candidat est libre d'ajouter des fonctions intermédiaires
(parse / normalize / validate / load) ; seuls les deux points d'entrée
ci-dessous sont attendus.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session


@dataclass
class ImportResult:
    """Compteurs d'un run d'import (alimentent la traçabilité / T5)."""

    created: int = 0
    updated: int = 0
    skipped: int = 0
    rejected: int = 0


def run_import(session: Session, path: str | Path) -> ImportResult:
    """Ingère un export CRM complet dans la base.

    Doit être :
      - **idempotent**   : rejouer le même fichier ne crée pas de doublon
        (pièges 1 & 6) ;
      - **multi-tenant** : aucune collision entre tenants (piège 2) ;
      - **robuste**      : les lignes invalides sont isolées et comptées,
        le run continue (pièges 3, 4, 5).

    TODO (T2-T3) :
      1. lire et normaliser le fichier (pandas) ;
      2. valider chaque enregistrement, isoler les rejets ;
      3. upsert par clé naturelle en gardant la version dont l'horodatage
         SOURCE est le plus récent (pas « dernier lu gagne »).
    """
    raise NotImplementedError("TODO T2-T3 : parse + validation + upsert")


def run_incremental(session: Session, path: str | Path) -> ImportResult:
    """Ingère un export **delta** : ne traite que les enregistrements plus
    récents que le high-water-mark déjà en base (par tenant).

    TODO (T4) :
      - déterminer le high-water-mark par tenant ;
      - ne traiter que le delta, en réutilisant la logique d'upsert ;
      - garantir la non-collision inter-tenant (piège 2).
    """
    raise NotImplementedError("TODO T4 : ingestion incrémentale (delta)")
