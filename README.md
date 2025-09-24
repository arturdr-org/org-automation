# org-automation (arturdrr-org)

Automação genérica para padronizar repositórios da organização `arturdrr-org`.

O script `automa_org.py` usa a API do GitHub para:
- listar todos os repositórios da organização
- criar/atualizar labels padrão
- criar uma issue de checklist de automação se não existir

Expansões futuras (sugestões):
- vincular/gerenciar Projects (v2) via GraphQL
- criar workflows padrão em repos faltantes
- aplicar templates (issues, PRs)

## Requisitos
- Python 3.8+
- requests (veja `requirements.txt`)
- Um token de acesso (PAT) com scopes: `repo`, `admin:org`, `project`, `workflow`

## Como configurar o segredo no repositório
Crie um segredo chamado `ORG_AUTOMATION_PAT` no repositório:
- GitHub → Repo → Settings → Secrets and variables → Actions → New repository secret
- Name: `ORG_AUTOMATION_PAT`
- Value: seu token (PAT)

## Como rodar
Localmente:
1. `python3 -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `export ORG_AUTOMATION_PAT=seu_token`
4. `python automa_org.py`

No GitHub Actions:
- O workflow `.github/workflows/automation-cron.yml` já está configurado para:
  - rodar diariamente (cron)
  - permitir execução manual (workflow_dispatch)
  - usar o segredo `ORG_AUTOMATION_PAT`

## Notas
- O token padrão do Actions (GITHUB_TOKEN) não tem permissões cross-repo/org suficientes. Por isso usamos `ORG_AUTOMATION_PAT`.
- Para Projects (v2) é necessário GraphQL e escopos adequados.
