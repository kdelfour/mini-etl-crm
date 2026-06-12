"""Tâche Celery d'import — TÂCHE T5 (stretch).

⚠️ La tâche est en at-least-once (`task_acks_late=True`) : elle peut être
rejouée si le worker tombe. L'import DOIT donc rester idempotent.
"""

from server.celery_app import celery_app
from server.database import SessionLocal  # noqa: F401  (à utiliser en T5)
from server.etl.pipeline import run_import  # noqa: F401  (à utiliser en T5)


@celery_app.task(name="etl.run_import")
def run_import_task(tenant: str, file: str) -> dict:
    """Exécute un import dans un worker Celery.

    TODO (T5) :
      - ouvrir une session (SessionLocal), appeler `run_import` ;
      - mettre à jour l'`import_run` (statut + compteurs) ;
      - renvoyer les compteurs sous forme de dict.
    """
    raise NotImplementedError("TODO T5 : exécuter l'import dans le worker")
