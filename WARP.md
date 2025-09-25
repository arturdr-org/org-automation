# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Comandos comuns (dev local)

- Preparar ambiente (Python 3.9+):
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

- Lint, formatação e tipos (espelha o pipeline CI):
  ```bash
  # checagens
  black --check --diff .
  isort --check-only --diff .
  flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
  flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
  mypy . --ignore-missing-imports || true

  # correções
  black .
  isort .
  ```

- Scans de segurança:
  ```bash
  bandit -r . -f json -o bandit-report.json || true
  safety check --json --output safety-report.json || true
  ```

- Testes (pytest):
  ```bash
  # todos os testes com cobertura
  pytest --cov=. --cov-report=xml --cov-report=html -v

  # um único teste por nodeid
  pytest path/para/test_file.py::TestClass::test_name -q

  # subconjunto por padrão de nome
  pytest -k "pattern" -v
  ```

- Build de pacote (igual ao job de release):
  ```bash
  pip install build twine
  python -m build
  twine check dist/*
  ```

- Scripts úteis (execução local):
  ```bash
  # demonstração do sistema
  python scripts/demo-ai-system.py

  # parser do manual de operações de IA (dry-run seguro)
  python scripts/ai-manual-parser.py --command "Verificar Status do Sistema" --dry-run

  # hub de integração com múltiplas AIs
  python scripts/ai-integration-hub.py list providers
  python scripts/ai-integration-hub.py list operations
  python scripts/ai-integration-hub.py start

  # validação de setup local
  python core/testing/setup_validator.py

  # automação modernizada (habilita Dependabot, CodeQL, etc.)
  # requer ORG_AUTOMATION_PAT/GITHUB_TOKEN configurados
  python scripts/modernized_automation.py
  ```

- Variáveis de ambiente relevantes:
  - ORG_AUTOMATION_PAT ou GITHUB_TOKEN (requerido para operações GitHub)
  - ORG_NAME (padrão: arturdr-org)
  - DRY_RUN=true para simular ações em scripts que suportam

## Arquitetura de alto nível

- Núcleo (core/)
  - automation/main.py: orquestra automações GitHub na organização (criação/atualização de labels, templates, workflows; proteção de branches). Lê configurações esperadas de YAML em common/config (labels.yml, branch_protection.yml, templates/). Expõe flags via env (ORG_NAME, ORG_AUTOMATION_PAT/GITHUB_TOKEN, DRY_RUN).
  - monitoring/health_check.py: coleta repositórios, verifica conformidade (labels, templates, workflows, proteção de branch), calcula percentuais e recomendações; consulta GitHub Actions para saúde de execuções.
  - testing/setup_validator.py: checagens locais (versão de Python, dependências, variáveis de ambiente, conectividade com GitHub, presença de arquivos de configuração e workflows obrigatórios).

- Módulos de domínio (modules/)
  - Ciclos funcionais encapsulados (cicd, security, quality, notifications) com READMEs próprios e templates associados quando aplicável.

- Integrações MCP (mcp-submodules/)
  - Entrypoints para Model Context Protocol (e.g., mcp_main.py) que viabilizam coordenação entre AIs e integrações GitHub.

- Scripts de automação (scripts/)
  - ai-integration-hub.py: coordenação multi-IA (listar provedores e operações; iniciar hub).
  - ai-manual-parser.py: interpreta comandos operacionais do “Manual de Operações AI”.
  - modernized_automation.py: aplica práticas modernas em repositórios (habilita Dependabot, CodeQL, auditorias, workflows de CI; configura proteção de branch via API GitHub).

- CI/CD (GitHub Actions)
  - .github/workflows/python-ci.yml: pipeline principal com estágios de qualidade (Black, isort, Flake8, MyPy), segurança (Bandit, Safety), testes (matriz 3.9–3.11 com coverage), build em releases e análise de segurança (CodeQL). Os comandos acima refletem esses estágios para execução local.
  - Workflows adicionais no diretório .github/workflows cobrem automação recorrente, auditorias e integrações externas.

## Notas de uso

- Muitos scripts interagem com a API do GitHub. Garanta que ORG_AUTOMATION_PAT ou GITHUB_TOKEN estejam presentes no ambiente antes de executá-los. Para execuções seguras, preferir DRY_RUN=true quando disponível.
- O diretório common/config é referenciado por core/automation/main.py e core/monitoring/health_check.py para YAMLs de configuração; ajuste conforme necessário no seu ambiente.
