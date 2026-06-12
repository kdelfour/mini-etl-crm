# Mini-ETL CRM — exercice pair programming

Bienvenue 👋 Cet exercice se fait **en binôme** (~60–90 min). Tu **conduis**
(driver), l'intervieweur **navigue**. Le principe est simple : tu **récupères
le projet sur ta machine**, tu **l'installes**, puis tu **le déroules en
expliquant à voix haute comment tu procèdes**. On part d'un squelette
**fourni et runnable** : tu ne perds pas de temps sur l'infra, on observe ton
**raisonnement** et ta **rigueur de production**.

> [!note] Pense à voix haute
> Tout au long de la séance, **explique comment tu procèdes** : tes hypothèses,
> ce que tu lis avant de coder, tes arbitrages (dette vs livraison), ce que tu
> vérifies. Le *chemin* compte plus que le nombre de tâches finies.

## 🎯 Objectif

Construire un petit pipeline qui **ingère un export CRM** (façon
Veeva/Salesforce) vers PostgreSQL, en respectant :

- l'**isolation par tenant** (plusieurs labos pharma dans la même base) ;
- l'**idempotence** (rejouer le même import ne crée pas de doublon) ;
- l'**ingestion incrémentale** (ne retraiter que le delta) ;
- la **traçabilité** du run.

## 🧰 Stack (déjà fournie)

Python 3.11 · Flask · **SQLAlchemy 2.0 + Alembic** · **pandas** ·
**Celery + RabbitMQ** (backend résultats PostgreSQL) · Redis (dispo) ·
pydantic / flask-pydantic · pytest. Versions calées sur le backend de prod.

## ⚙️ Prérequis

- [Python 3.11](https://www.python.org/downloads/) (le projet est calé sur 3.11)
- [Docker](https://docs.docker.com/get-docker/) (+ plugin `docker compose` v2)
- [Poetry](https://python-poetry.org/docs/#installation)

> `make check` vérifie d'un coup que tout est présent — y compris que le
> **démon Docker tourne**. C'est aussi la première chose que fait `make install`.

## 📥 Récupérer le projet

```bash
git clone https://github.com/kdelfour/mini-etl-crm.git
cd mini-etl-crm
```

## 🚀 Installer & lancer

```bash
make check          # vérifie python 3.11, poetry, docker + compose (démon up)
make install        # ↑ check, puis deps (poetry, venv dans .venv/) + pull des images Docker
make up             # db + rabbitmq + redis — images déjà pull, démarrage immédiat
make migrate        # applique les migrations (une fois la T1 écrite)
make api            # API Flask sur http://127.0.0.1:8000
make worker         # worker Celery (pour la T5)
make test           # pytest
```

`make help` liste toutes les cibles.

> `make install` **vérifie d'abord les prérequis** (cf. `make check`), installe
> les dépendances **et pré-télécharge les images Docker** — `make up` est alors
> quasi instantané. Si un prérequis manque, l'install s'arrête net avec la
> marche à suivre.

> Les services tournent sur des **ports décalés** (db `5440`, rabbitmq
> `5673`, redis `6380`) pour coexister avec un autre backend déjà lancé
> en local. L'API Flask écoute sur `8000`.

## 📦 Données fournies

Dans `data/`, deux fichiers et deux tenants — **avec des pièges volontaires** :

- `crm_full_2026-06-01.json` — chargement initial (tenant `pharma-alpha`).
- `crm_delta_2026-06-02.json` — run incrémental (tenant `pharma-beta`).

> Les pièges (doublon, collision inter-tenant, champ requis manquant,
> date invalide, interaction orpheline, re-run) sont détaillés dans
> l'énoncé facilitateur. Ils sont là pour être trouvés : prends le temps
> de regarder la donnée avant de coder.

## 📋 Tâches (must-have → stretch)

On s'arrête où on en est ; ce qui compte est la **qualité du chemin**.

1. **T1 — Modèle + migration (multi-tenant).** Tables `account` /
   `interaction` (+ `import_run` plus tard), avec la **bonne clé
   d'unicité** et la FK. Migration Alembic (`make revision m="..."`).
   → `server/etl/models.py`
2. **T2 — Parse + normalisation (pandas) + validation.** Lire, normaliser,
   **valider** chaque enregistrement, **isoler** les lignes invalides
   sans tout faire échouer. → `server/etl/pipeline.py`
3. **T3 — Load idempotent (upsert).** Insérer/mettre à jour par clé
   naturelle en gardant la version la plus **récente** (horodatage
   source). Rejouer = no-op. → `run_import`
4. **T4 — Ingestion incrémentale.** Sur le delta, ne traiter que ce qui
   est plus récent que le high-water-mark par tenant. → `run_incremental`
5. **T5 (stretch) — Async + traçabilité.** `POST /imports` →
   tâche Celery + `import_run` (statut, compteurs).
   → `server/etl/api.py`, `server/etl/tasks.py`
6. **T6 (stretch) — Tests.** Un cas **succès** (idempotence) et un cas
   **donnée sale** (rejet). → `tests/test_pipeline.py`

## ✍️ Ce que tu écris vs ce qui est fourni

| Fourni (ne pas réécrire) | À écrire (toi) |
|---|---|
| compose, config, logging, session, app Flask, app Celery, scaffolding Alembic, données, fixtures pytest | les modèles (T1), le pipeline parse/load/incrémental (T2-T4), l'endpoint + la tâche (T5), les tests (T6) |

Les points d'entrée à compléter sont balisés `TODO` et lèvent
`NotImplementedError`. Les fonctions du pipeline reçoivent une `Session`
SQLAlchemy en paramètre (pour la testabilité).

## 🗂️ Structure

```
mini-etl-crm/
├─ docker-compose.yml        # db + rabbitmq + redis
├─ Makefile                  # check / install / up / migrate / api / worker / test
├─ CONTRIBUTING.md           # flux de travail + conventions de code
├─ CODE_OF_CONDUCT.md        # cadre de bienveillance de la séance
├─ scripts/
│  ├─ preflight.sh           # vérif des prérequis (make check)
│  └─ run_api.py, run_worker.py
├─ alembic.ini, migrations/  # scaffolding Alembic (tu écris la 1re révision)
├─ data/                     # exports CRM (avec pièges)
├─ server/
│  ├─ config.py              # config (classes + env), URLs db/broker/redis
│  ├─ database.py            # engine, SessionLocal, Base, BaseModel
│  ├─ logging_setup.py       # structlog JSON
│  ├─ app.py                 # fabrique Flask
│  ├─ celery_app.py          # Celery (acks_late = at-least-once)
│  └─ etl/
│     ├─ models.py           # ← T1
│     ├─ schemas.py          # pydantic API (fourni)
│     ├─ pipeline.py         # ← T2-T4 (cœur)
│     ├─ api.py              # ← T5
│     └─ tasks.py            # ← T5
└─ tests/                    # conftest (fourni) + test_pipeline.py (← T6)
```

## 📚 Conventions & savoir-vivre

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — comment on travaille ici : flux Git,
  conventions de code (ruff/mypy, type hints, logging structuré, migrations),
  checklist avant de proposer un changement.
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — le cadre de bienveillance de la
  séance.

Bon courage — et n'hésite pas à **penser à voix haute**. 🙂
