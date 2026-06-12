"""Application Celery.

Reproduit le choix du monolith (`server/queues/setup.py`) :
broker = RabbitMQ (amqp), backend de résultats = PostgreSQL (`db+...`).

`task_acks_late=True` est volontaire : la tâche est en **at-least-once**
(elle peut être rejouée si le worker meurt). C'est tout l'intérêt de
l'exercice : l'import doit rester **idempotent**.
"""

from celery import Celery

from server.config import config

celery_app = Celery(
    "crm_etl",
    broker=config.broker_url,
    backend=f"db+{config.url}",
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue="default",
    task_track_started=True,
    result_extended=True,
)

# Découverte automatique des tâches (server/etl/tasks.py).
celery_app.autodiscover_tasks(["server.etl"])
