"""Logging structuré (structlog), version allégée de `server/sb_logger`.

Sortie JSON, prête pour Datadog. Pas de dépendance dure à `ddtrace`
(l'exercice n'en a pas besoin).
"""

import logging

import structlog


def configure_logging(level: int = logging.INFO) -> None:
    """Configure structlog en sortie JSON."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "etl") -> structlog.stdlib.BoundLogger:
    """Renvoie un logger structuré."""
    return structlog.get_logger(name)
