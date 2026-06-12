"""Configuration de l'exercice.

Calquée sur `server/config/sql.py` du monolith : classes + fallback sur
les variables d'environnement, propriété `url` qui construit la chaîne
SQLAlchemy au même format (`postgresql+psycopg2://...`).
"""

import os


class Common:
    """Valeurs de base (surchargées par environnement)."""

    SQL_USER = ""
    SQL_PASSWORD = ""  # nosec
    SQL_HOST = ""
    SQL_PORT = ""
    SQL_DATABASE = ""

    RABBITMQ_USER = "guest"
    RABBITMQ_PASSWORD = "guest"  # nosec
    RABBITMQ_HOST = "localhost"
    RABBITMQ_PORT = "5672"
    RABBITMQ_VHOST = "/"

    REDIS_HOST = "localhost"
    REDIS_PORT = "6379"
    REDIS_DB = "0"

    @property
    def url(self) -> str:
        """URL SQLAlchemy (même format que le monolith)."""
        return (
            f"postgresql+psycopg2://{self.SQL_USER}:{self.SQL_PASSWORD}@"
            f"{self.SQL_HOST}:{self.SQL_PORT}/{self.SQL_DATABASE}"
        )

    @property
    def broker_url(self) -> str:
        """URL du broker RabbitMQ (Celery)."""
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@"
            f"{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"
            f"{self.RABBITMQ_VHOST}"
        )

    @property
    def redis_url(self) -> str:
        """URL Redis (cache, si besoin)."""
        return (
            f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        )


class Development(Common):
    """Environnement local (valeurs alignées sur le docker-compose)."""

    SQL_USER: str = os.getenv("SQL_USER", "etl")
    SQL_PASSWORD: str = os.getenv("SQL_PASSWORD", "etl")  # nosec
    SQL_HOST: str = os.getenv("SQL_HOST", "localhost")
    SQL_PORT: str = os.getenv("SQL_PORT", "5440")
    SQL_DATABASE: str = os.getenv("SQL_DATABASE", "crm_etl")

    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "etl")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "etl")  # nosec
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5673")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6380")
    REDIS_DB = os.getenv("REDIS_DB", "0")


config = Development()
