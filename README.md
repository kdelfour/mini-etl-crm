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

Dans `data/`, **deux exports** et **deux tenants** (= deux labos pharma) :

| Fichier | Rôle | Tenant |
|---|---|---|
| `crm_full_2026-06-01.json` | chargement **initial** (full) | `pharma-alpha` |
| `crm_delta_2026-06-02.json` | run **incrémental** (delta) | `pharma-beta` |

Chaque fichier a la forme `{ "tenant": ..., "accounts": [...], "interactions": [...] }`.
Un enregistrement ressemble à :

```jsonc
{
  "tenant": "pharma-alpha",
  "accounts": [
    {
      "external_id": "ACC-1001",   // identifiant métier côté CRM
      "first_name": "Marie",
      "last_name": "Durand",
      "specialty": "Cardiology",
      "email": "m.durand@chu.fr",
      "territory": "FR-PACA",
      "updated_at": "2026-05-30T10:00:00Z"   // horodatage SOURCE (CRM), ISO 8601
    }
  ],
  "interactions": [
    {
      "external_id": "CALL-55",
      "account_external_id": "ACC-1001",   // référence un account.external_id
      "channel": "VISIT",
      "occurred_at": "2026-05-29",
      "rep": "rep-12",
      "updated_at": "2026-05-29T18:00:00Z"
    }
  ]
}
```

Champs : **account** = `external_id`, `first_name`, `last_name`, `specialty`,
`email`, `territory`, `updated_at` ; **interaction** = `external_id`,
`account_external_id`, `channel`, `occurred_at`, `rep`, `updated_at`. À toi de
décider quels champs sont requis et ta politique de validation.

> [!warning] Le jeu de données contient des cas limites **volontaires** (≈6) — à
> repérer en regardant la donnée **avant** de coder. Ils couvrent : doublon dans
> un même fichier, même `external_id` chez deux tenants, champ requis manquant,
> date invalide, interaction orpheline (compte inexistant), re-run du même
> fichier. Rien ne doit faire planter le run en entier.

> ⚠️ **Deux `updated_at` à ne pas confondre** : celui de l'export (horodatage
> **source**, dans le JSON) et celui de `BaseModel` (date d'audit de la **ligne**,
> cf. `server/database.py`). Le premier sert à départager les versions.

## 📋 Énoncé détaillé — tâches (must-have → stretch)

On s'arrête où on en est ; ce qui compte est la **qualité du chemin**, pas le
nombre de tâches finies. Pour chaque tâche : **objectif**, **où écrire**, et les
**critères de réussite** (definition of done). Les **décisions de conception**
(clé, stratégie d'upsert, reprise…) sont à toi — c'est le cœur de ce qu'on observe.

> 💡 Avant la T5, pas besoin de l'API : tu peux exercer `run_import(session, path)`
> directement depuis un test `pytest` ou un `poetry run python`. Les fonctions du
> pipeline renvoient un `ImportResult(created, updated, skipped, rejected)`.

### T1 — Modèle de données + migration (must-have)
- **Objectif.** Modéliser `account` et `interaction` (puis `import_run` en T5)
  pour un contexte **multi-tenant**, et générer la **migration Alembic**.
- **Où.** `server/etl/models.py` · migration : `make revision m="..."` puis
  `make migrate`.
- **Critères de réussite.**
  - Les colonnes couvrent les champs de l'export (cf. § Données).
  - **Unicité multi-tenant** : un même `external_id` peut coexister chez deux
    tenants **sans collision**, mais reste unique **au sein d'un** tenant.
  - **FK** `interaction → account` cohérente (et une stratégie pour une
    interaction qui pointe vers un compte absent — cf. T2).
  - L'**horodatage source** est stocké à part de l'`updated_at` d'audit.
  - `make migrate` s'applique sans erreur sur une base vierge.

### T2 — Parse, normalisation (pandas) & validation (must-have)
- **Objectif.** Lire un export, **normaliser** (pandas), **valider** chaque
  enregistrement et **isoler** les lignes invalides sans faire échouer le run.
- **Où.** `server/etl/pipeline.py` (fonctions intermédiaires libres :
  parse / normalize / validate).
- **Critères de réussite.**
  - Une ligne invalide (champ requis manquant, date/type incorrect) est
    **rejetée et comptée** (`rejected`), le run **continue**.
  - Une interaction orpheline (compte inexistant) est gérée proprement (rejet ou
    différé) — **jamais** d'`IntegrityError` brute qui remonte.
  - Les compteurs `created / updated / skipped / rejected` reflètent la réalité.

### T3 — Chargement idempotent / upsert (must-have)
- **Objectif.** Insérer/mettre à jour par **clé naturelle** en conservant la
  version dont l'**horodatage source** est le plus récent. Rejouer = **no-op**.
- **Où.** `run_import(session, path)` dans `pipeline.py`.
- **Critères de réussite.**
  - 1ᵉʳ passage : N créés ; **2ᵉ passage du même fichier** : `created == 0` **et**
    `updated == 0` (idempotent).
  - Deux versions d'un même enregistrement dans un fichier → c'est la **plus
    récente au sens de l'horodatage source** qui l'emporte (pas « la dernière lue »).
  - Aucune collision entre tenants.

### T4 — Ingestion incrémentale (must-have)
- **Objectif.** Sur un export **delta**, ne traiter que les enregistrements
  **plus récents** que ce qui est déjà en base, **par tenant**.
- **Où.** `run_incremental(session, path)` dans `pipeline.py`.
- **Critères de réussite.**
  - Les enregistrements déjà connus et non modifiés ne sont **pas** retraités.
  - Isolation tenant préservée (un `external_id` partagé n'écrase pas l'autre).
  - Réfléchis à la **reprise** si un run précédent s'est interrompu en cours.

### T5 — Async + traçabilité (stretch)
- **Objectif.** Déclencher l'import via l'**API**, l'exécuter dans un **worker
  Celery**, et **tracer** le run.
- **Où.** `server/etl/api.py` (endpoint) · `server/etl/tasks.py` (tâche) ·
  `import_run` dans `models.py`.
- **Contrat d'API** (schémas fournis dans `server/etl/schemas.py`) :
  ```http
  POST /imports
  ```
  ```jsonc
  // requête (ImportRequest)
  { "tenant": "pharma-alpha", "file": "data/crm_full_2026-06-01.json" }
  // réponse (ImportRunResponse)
  { "id": "...", "tenant": "pharma-alpha", "status": "queued",
    "created": 0, "updated": 0, "skipped": 0, "rejected": 0 }
  ```
- **Critères de réussite.**
  - L'endpoint **enfile** une tâche Celery (`run_import_task.delay(...)`) et
    renvoie le run, sans bloquer sur l'import.
  - La tâche est **idempotente** : `acks_late=True` ⇒ **at-least-once**, donc un
    rejeu ne doit pas créer de doublon.
  - `import_run` persiste `status` + compteurs + horodatages (traçabilité).

### T6 — Tests (stretch)
- **Objectif.** Prouver les deux propriétés clés du pipeline.
- **Où.** `tests/test_pipeline.py`. La fixture **`db_session`** (fournie) donne
  une base PostgreSQL de test, **vidée entre chaque test**.
- **Critères de réussite.**
  - Un test **succès** : deux imports successifs → **idempotence** (compteurs au
    2ᵉ passage à zéro).
  - Un test **donnée sale** : au moins une ligne part en **rejet**, le run continue.
  - `make test` au vert.

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
