#!/usr/bin/env bash
# Préflight : vérifie que l'outillage minimal est présent AVANT l'install.
# Calé sur la stack du monolith de prod : Python 3.11, Poetry, Docker + Compose v2.
# Appelé par `make check` et en première étape de `make install`.
set -uo pipefail

# Couleurs (désactivées hors terminal)
if [[ -t 1 ]]; then
  RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; BOLD=$'\033[1m'; RESET=$'\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; BOLD=''; RESET=''
fi

ok()   { printf "  ${GREEN}✓${RESET} %s\n" "$1"; }
warn() { printf "  ${YELLOW}!${RESET} %s\n" "$1"; }
ko()   { printf "  ${RED}✗${RESET} %s\n" "$1"; }

errors=0

printf "${BOLD}Vérification des prérequis…${RESET}\n"

# --- Python 3.11 -----------------------------------------------------------
if command -v python3 >/dev/null 2>&1; then
  pyver="$(python3 -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])')"
  read -r pymaj pymin <<<"$(python3 -c 'import sys;print(sys.version_info[0], sys.version_info[1])')"
  if [[ "$pymaj" -gt 3 || ( "$pymaj" -eq 3 && "$pymin" -ge 11 ) ]]; then
    if [[ "$pymaj" -eq 3 && "$pymin" -eq 11 ]]; then
      ok "Python ${pyver}"
    else
      warn "Python ${pyver} — le projet cible 3.11 (pyproject : >=3.11,<3.12). Poetry tentera de trouver un interpréteur 3.11."
    fi
  else
    ko "Python ${pyver} trop ancien (minimum 3.11) — https://www.python.org/downloads/"
    errors=$((errors+1))
  fi
else
  ko "python3 introuvable (minimum 3.11) — https://www.python.org/downloads/"
  errors=$((errors+1))
fi

# --- Poetry ----------------------------------------------------------------
if command -v poetry >/dev/null 2>&1; then
  ok "$(poetry --version 2>/dev/null)"
else
  ko "Poetry introuvable — https://python-poetry.org/docs/#installation"
  errors=$((errors+1))
fi

# --- Docker + démon + Compose v2 -------------------------------------------
if command -v docker >/dev/null 2>&1; then
  dver="$(docker version --format '{{.Client.Version}}' 2>/dev/null)"
  [[ -z "$dver" ]] && dver="$(docker --version 2>/dev/null)"
  ok "Docker ${dver}"

  if docker info >/dev/null 2>&1; then
    ok "Démon Docker démarré"
  else
    ko "Le démon Docker ne répond pas — démarre Docker Desktop / le service docker."
    errors=$((errors+1))
  fi

  if docker compose version >/dev/null 2>&1; then
    ok "Docker Compose v2 ($(docker compose version --short 2>/dev/null))"
  else
    ko "Plugin 'docker compose' (v2) introuvable — https://docs.docker.com/compose/install/"
    errors=$((errors+1))
  fi
else
  ko "Docker introuvable — https://docs.docker.com/get-docker/"
  errors=$((errors+1))
fi

echo
if [[ "$errors" -gt 0 ]]; then
  printf "${RED}${BOLD}%d prérequis manquant(s).${RESET} Corrige les points ci-dessus puis relance ${BOLD}make install${RESET}.\n" "$errors"
  exit 1
fi
printf "${GREEN}${BOLD}Tous les prérequis sont présents.${RESET} → ${BOLD}make install${RESET}\n"
