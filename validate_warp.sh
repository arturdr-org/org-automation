#!/usr/bin/env bash
# validate_warp.sh — Validação local dos comandos do WARP.md
# Alinha checagens com o pipeline .github/workflows/python-ci.yml

set -euo pipefail

info() { printf "\033[1;34m[info]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[warn]\033[0m %s\n" "$*"; }
error() { printf "\033[1;31m[error]\033[0m %s\n" "$*"; }

# Detectar e ativar venv
if [[ -d .venv ]]; then
  info "Ativando ambiente virtual em .venv"
  # shellcheck disable=SC1091
  source .venv/bin/activate
else
  warn "Nenhum .venv encontrado. Criando e instalando dependências mínimas..."
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

info "Atualizando pip"
python -m pip install --upgrade pip

# Instalar dependências do projeto (se existirem)
if [[ -f requirements.txt ]]; then
  info "Instalando requirements.txt"
  pip install -r requirements.txt
fi
if [[ -f requirements-dev.txt ]]; then
  info "Instalando requirements-dev.txt"
  pip install -r requirements-dev.txt
fi

# Ferramentas usadas no CI
info "Instalando ferramentas de qualidade e segurança"
pip install black isort flake8 mypy bandit safety pytest pytest-cov build twine

# Lint/format/type-check (espelha o CI)
info "Executando Black (check/diff)"
black --check --diff .

info "Executando isort (check/diff)"
isort --check-only --diff .

info "Executando Flake8 (regras rígidas e estatísticas)"
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

info "Executando MyPy (ignorando imports ausentes)"
# MyPy pode falhar por imports opcionais; acompanhe os avisos localmente
mypy . --ignore-missing-imports || warn "MyPy retornou avisos (permitido localmente)"

# Scans de segurança (tolerantes como no CI)
info "Executando Bandit"
bandit -r . -f json -o bandit-report.json || warn "Bandit encontrou issues"

info "Executando Safety"
safety check --json --output safety-report.json || warn "Safety encontrou vulnerabilidades"

# Testes
info "Executando testes com cobertura"
pytest --cov=. --cov-report=xml --cov-report=term-missing -v

# Build e validação do pacote
info "Build do pacote (se aplicável)"
python -m build || warn "Build falhou (ok se o projeto não estiver empacotado)"

if compgen -G "dist/*" > /dev/null; then
  info "Verificando artefatos com twine"
  twine check dist/*
else
  warn "Diretório dist/ inexistente; pulando 'twine check'"
fi

info "Validação concluída. Relatórios: bandit-report.json, safety-report.json, coverage.xml"
