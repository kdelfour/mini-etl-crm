"""Endpoint d'import — TÂCHE T5 (stretch).

Le candidat câble ici `POST /imports` : valider la requête
(flask-pydantic), enfiler une tâche Celery, renvoyer le run.
"""

from flask import Blueprint
from flask_pydantic import validate

from server.etl.schemas import ImportRequest, ImportRunResponse

imports_bp = Blueprint("imports", __name__, url_prefix="/imports")


@imports_bp.route("", methods=["POST"])
@validate()
def create_import(body: ImportRequest) -> ImportRunResponse:
    """Déclenche un import CRM (asynchrone via Celery).

    TODO (T5) :
      - persister un `import_run` à l'état "queued" ;
      - enfiler `run_import_task.delay(tenant, file)` ;
      - renvoyer le run (id, statut).
    """
    raise NotImplementedError("TODO T5 : enfiler la tâche Celery d'import")
