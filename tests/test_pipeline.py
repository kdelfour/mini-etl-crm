"""Tests du pipeline — TÂCHE T6 (stretch, à compléter par le candidat).

Au moins : un test de **succès** (idempotence) et un test de **donnée
sale** (rejet). Les squelettes ci-dessous donnent la cible ; ils sont
marqués `skip` tant qu'ils ne sont pas implémentés.
"""

import pytest

from server.etl.pipeline import run_import

FULL = "data/crm_full_2026-06-01.json"


@pytest.mark.skip(reason="TODO T6 — à implémenter par le candidat")
def test_import_is_idempotent(db_session):
    """Rejouer le même fichier ne crée pas de doublon (pièges 1 & 6)."""
    run_import(db_session, FULL)
    second = run_import(db_session, FULL)
    assert second.created == 0
    assert second.updated == 0


@pytest.mark.skip(reason="TODO T6 — à implémenter par le candidat")
def test_dirty_rows_are_rejected(db_session):
    """Les lignes invalides partent en rejet, le run continue (pièges 3-5)."""
    result = run_import(db_session, FULL)
    # `last_name: null`, `updated_at: "bad-date"`, compte orphelin ACC-9999
    assert result.rejected >= 1
