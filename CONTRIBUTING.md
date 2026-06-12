# Contribuer & conventions de code

Ce dépôt est un **exercice de pair programming** pour le poste *Senior Backend
Engineer*. Pendant la séance, « contribuer » veut dire : **dérouler l'exercice
en expliquant tes choix**, sur la même stack et avec les mêmes conventions que
notre backend de production (`monolith-back`). Ce document décrit **comment on
travaille ici** — autant le flux que les conventions de code attendues.

## 🚀 Mise en route

Voir le [README](README.md). En résumé :

```bash
make check       # vérifie python 3.11, poetry, docker + compose
make install     # check + deps (poetry) + pull des images Docker
make up          # services (db / rabbitmq / redis)
make test        # pytest
```

## 🧭 Flux de travail (pair pro)

- **Rôles** : tu **conduis** (driver), l'intervieweur **navigue**. On code dans
  ton IDE ou le nôtre, peu importe.
- **Pense à voix haute** : explicite tes hypothèses, ce que tu lis avant de
  coder, tes arbitrages. On préfère un raisonnement clair sur 3 tâches à 6
  tâches expédiées.
- **Avance par petits pas** : un changement cohérent à la fois, vérifiable
  (`make lint && make test`).
- **Regarde la donnée avant de coder** : `data/` contient des pièges volontaires.

## 🌿 Conventions Git

- **Branches** : `feat/...`, `fix/...`, `chore/...`, `test/...`.
- **Commits** façon *Conventional Commits* :
  `type(scope): résumé à l'impératif`
  (`feat(etl): upsert idempotent par (tenant, external_id)`).
- Commits **petits et atomiques**, message qui explique le *pourquoi*, pas
  seulement le *quoi*.

## 🐍 Conventions de code

- **Python 3.11**, **type hints obligatoires** : `mypy` est configuré en
  `disallow_untyped_defs` (cf. `pyproject.toml`). Toute fonction est typée.
- **Lint & format : Ruff**, ligne **78 colonnes**, règles `UP`, `SIM`, `PTH`,
  `I` (imports triés). `make lint` doit être vert.
- **Logging structuré** via `structlog` (JSON) — **jamais de `print`**.
- **SQLAlchemy 2.0** (style moderne) ; **schéma versionné par Alembic**, pas de
  `Base.metadata.create_all` en dehors des fixtures de test.
- **Validation** des entrées via `pydantic` / `flask-pydantic` ; on isole les
  lignes invalides, on ne fait pas planter tout un run.
- **Config par l'environnement** (`pydantic-settings`) — **aucun secret en
  dur**, on s'appuie sur `.env` (cf. `.env.example`).
- **Idempotence & multi-tenant** : clé naturelle `(tenant, external_id)`,
  requêtes cloisonnées par tenant, upsert avec garde sur l'horodatage source.
- **Tests** avec `pytest` (`make test`) : au moins un cas **succès** et un cas
  **échec/donnée sale** quand tu touches au pipeline.

## ✅ Avant de proposer un changement

```bash
make lint     # ruff + mypy au vert
make test     # pytest au vert
```

Un changement se présente avec : ce qu'il fait, **pourquoi**, et comment tu l'as
vérifié.

## 🤝 Savoir-vivre

La séance suit le [Code de conduite](CODE_OF_CONDUCT.md) : bienveillance,
écoute, et droit à l'erreur. On débloque volontiers sur la **syntaxe** ; les
**décisions de conception** (clé, idempotence, multi-tenant), on veut te voir
les prendre.
