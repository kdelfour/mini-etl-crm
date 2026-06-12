"""Modèles ETL — TÂCHE T1 (à compléter par le candidat).

Les champs proviennent de l'export CRM (cf. `data/crm_full_2026-06-01.json`).
On hérite de `BaseModel` (id/created_at/updated_at) + `Base`, comme dans
le monolith.

⚠️ Points de conception laissés au candidat (volontairement non fournis) :
  - la clé naturelle / contrainte d'unicité en contexte **multi-tenant**
    (deux labos peuvent partager le même `external_id`) ;
  - où stocker l'horodatage **source** (`updated_at` du CRM) sans le
    confondre avec l'`updated_at` d'audit de `BaseModel` ;
  - la FK `interaction -> account` et la gestion des **orphelins**.
"""

from server.database import Base, BaseModel


class Account(BaseModel, Base):
    __tablename__ = "account"

    # TODO (T1) — colonnes : tenant, external_id, first_name, last_name,
    #   specialty, email, territory, + horodatage SOURCE.
    # TODO (T1) — __table_args__ : contrainte d'unicité multi-tenant.


class Interaction(BaseModel, Base):
    __tablename__ = "interaction"

    # TODO (T1) — colonnes : tenant, external_id, account_external_id,
    #   channel, occurred_at, rep, + horodatage SOURCE.
    # TODO (T1) — FK vers account + contrainte d'unicité.


class ImportRun(BaseModel, Base):
    __tablename__ = "import_run"

    # TODO (T5) — tenant, status, compteurs created/updated/skipped/
    #   rejected, horodatages début/fin. Sert la traçabilité du run.
