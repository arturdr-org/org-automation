# org-automation (arturdrr-org)

Automação genérica para padronizar repositórios da organização `arturdrr-org`.

O script `automa_org.py` usa as APIs REST e GraphQL do GitHub para:
- listar todos os repositórios da organização
- criar/atualizar labels padrão e personalizadas
- inserir templates padrão (issues e PRs) sem sobrescrever os existentes
- criar workflow básico de CI (YAML lint) quando ausente
- criar/vincular uma issue de checklist de automação
- vincular issues ao Project (v2) da organização via GraphQL

## Requisitos
- Python 3.8+
- requests (veja `requirements.txt`)
- Um token de acesso (PAT) com scopes: `repo`, `admin:org`, `project`, `read:project`, `workflow`

## Variáveis de ambiente
- `ORG_NAME` (opcional): organização alvo. Padrão: `arturdrr-org`
- `PROJECT_NUMBER` (opcional): número do Project v2 da organização. Padrão: `1`
- `ORG_AUTOMATION_PAT` (recomendado) ou `GITHUB_TOKEN`: token para autenticação

## Como configurar o segredo no repositório
Crie um segredo chamado `ORG_AUTOMATION_PAT` no repositório:
- GitHub → Repo → Settings → Secrets and variables → Actions → New repository secret
- Name: `ORG_AUTOMATION_PAT`
- Value: seu token (PAT)

Via CLI (supondo variável exportada no ambiente):
```
printf "%s" "$ORG_AUTOMATION_PAT" | gh secret set ORG_AUTOMATION_PAT --repo arturdrr-org/org-automation --body -
```

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
- Para Projects (v2) é necessário GraphQL e escopos `project` e `read:project`.
- O script evita sobrescrever arquivos existentes; caso precise atualizar, faça via PR dedicada.
