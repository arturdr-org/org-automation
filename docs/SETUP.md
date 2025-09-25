# 🛠️ Guia de Configuração Completa

> Instruções passo a passo para configurar o sistema de automação da organização arturdr-org.

## 📋 Pré-requisitos

### 🔧 Ferramentas Necessárias

- **Git**: Para clonar o repositório
- **Python 3.8+**: Runtime principal
- **GitHub CLI** (opcional): Para configuração via linha de comando
- **Permissões de Admin**: Na organização GitHub

### 🔑 Permissões GitHub

O sistema precisa das seguintes permissões:

- `admin:org` - Gerenciar organização
- `repo` - Acesso completo aos repositórios
- `workflow` - Gerenciar GitHub Actions
- `read:project` - Ler projetos
- `write:project` - Escrever projetos

## 🚀 Instalação Passo a Passo

### 1️⃣ Clonar e Configurar Ambiente

```bash
# Clonar o repositório
git clone https://github.com/arturdr-org/org-automation.git
cd org-automation

# Criar ambiente virtual Python
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2️⃣ Configurar Autenticação

#### Opção A: GitHub App (Recomendado)

1. **Criar GitHub App**:
   - Vá para `Settings` → `Developer settings` → `GitHub Apps`
   - Clique em `New GitHub App`
   - Configure:
     - **Name**: `org-automation-arturdr`
     - **Homepage URL**: `https://github.com/arturdr-org/org-automation`
     - **Webhook**: Desabilitar

2. **Permissões necessárias**:
   ```
   Repository permissions:
   - Contents: Read & Write
   - Issues: Read & Write  
   - Metadata: Read
   - Pull requests: Read & Write
   - Actions: Write
   
   Organization permissions:
   - Members: Read
   - Administration: Write
   ```

3. **Instalar na Organização**:
   - Após criar o App, clique em `Install App`
   - Selecione a organização `arturdr-org`
   - Escolha `All repositories` ou selecione específicos

4. **Configurar Secrets**:
   ```bash
   # No repositório org-automation
   gh secret set ORG_APP_ID --body "123456"
   gh secret set ORG_APP_PRIVATE_KEY --body "$(cat path/to/private-key.pem)"
   ```

#### Opção B: Personal Access Token

1. **Criar PAT**:
   - Vá para `Settings` → `Developer settings` → `Personal access tokens` → `Tokens (classic)`
   - Gere novo token com os escopos necessários

2. **Configurar Secret**:
   ```bash
   gh secret set ORG_AUTOMATION_PAT --body "ghp_your_token_here"
   ```

### 3️⃣ Configurar Variáveis de Ambiente

```bash
# Para desenvolvimento local
cat > .env << EOF
ORG_NAME=arturdr-org
PROJECT_NUMBER=1
ORG_AUTOMATION_PAT=your_token_here
DRY_RUN=true
EOF

# Carregar variáveis
source .env
```

### 4️⃣ Personalizar Configurações

#### Labels da Organização

Edite `config/labels.yml` para adicionar labels específicas:

```yaml
org_labels:
  # Suas labels personalizadas
  - name: "área:específica"
    color: "ff6b6b"  
    description: "Área específica da sua organização"
```

#### Proteções de Branch

Ajuste `config/branch_protection.yml` conforme suas necessidades:

```yaml
branch_protection:
  main:
    required_status_checks:
      strict: true
      contexts:
        - "ci-basic-workflow"
        - "seus-checks-personalizados"
```

#### Templates

Personalize templates em `config/templates/`:

- `bug_report.md` - Template para bugs
- `feature_request.md` - Template para features
- `pull_request_template.md` - Template para PRs

### 5️⃣ Teste de Configuração

```bash
# Teste básico (DRY-RUN)
DRY_RUN=true python enhanced_automation.py

# Teste de monitoramento
python monitoring.py

# Validar configurações YAML
python -c "import yaml; yaml.safe_load(open('config/labels.yml')); print('✅ Configurações válidas')"
```

## 🔄 Configuração dos Workflows

### Workflow Principal

O arquivo `.github/workflows/enhanced-automation.yml` está configurado para:

- **Execução automática**: Diariamente às 2:00 UTC
- **Execução manual**: Via workflow_dispatch
- **Trigger em mudanças**: Quando arquivos de config são alterados

### Workflow de Monitoramento

O arquivo `.github/workflows/health-monitoring.yml` executa:

- **Health checks**: 2x por dia (6:00 e 18:00 UTC)
- **Relatórios semanais**: Segundas-feiras às 6:00 UTC
- **Alertas automáticos**: Quando problemas críticos são detectados

## 🎯 Configuração Avançada

### Personalizar Automações

Para adicionar novas automações, edite `enhanced_automation.py`:

```python
def custom_automation(self, repo_name: str) -> None:
    """Sua automação personalizada."""
    # Implementar lógica personalizada
    pass

# Adicionar no método process_repository:
def process_repository(self, repo: Dict) -> None:
    # ... código existente ...
    
    # 5. Sua automação personalizada
    self.custom_automation(repo_name)
```

### Configurar Notificações

Para receber notificações por email/Slack, configure webhooks:

```yaml
# Em .github/workflows/health-monitoring.yml
- name: Notificar Slack
  if: needs.health-check.outputs.health-status == 'critical'
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Filtrar Repositórios

Para aplicar automação apenas a repositórios específicos:

```python
# Em enhanced_automation.py
EXCLUDED_REPOS = ['.github', 'docs', 'archived-repo']

def should_process_repo(self, repo: Dict) -> bool:
    return (
        not repo.get('archived', False) and
        repo['name'] not in EXCLUDED_REPOS and
        not repo['name'].startswith('temp-')
    )
```

## 🔧 Solução de Problemas

### Problemas Comuns

#### 1. Erro de Permissões

```bash
# Verificar permissões do token
curl -H "Authorization: token $ORG_AUTOMATION_PAT" \
     https://api.github.com/user

# Verificar acesso à organização
curl -H "Authorization: token $ORG_AUTOMATION_PAT" \
     https://api.github.com/orgs/arturdr-org/repos
```

#### 2. Falha na Automação

```bash
# Executar com logs detalhados
PYTHONPATH=. python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from enhanced_automation import OrganizationAutomation
automation = OrganizationAutomation()
automation.run()
"
```

#### 3. Problemas de Configuração YAML

```bash
# Validar YAML
python -c "
import yaml
try:
    yaml.safe_load(open('config/labels.yml'))
    print('✅ Labels YAML válido')
except Exception as e:
    print(f'❌ Erro no YAML: {e}')
"
```

### Logs e Debugging

#### Ativar Debug

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python enhanced_automation.py
```

#### Verificar Logs de Workflow

1. Vá para `Actions` no GitHub
2. Clique na execução do workflow
3. Expanda os steps para ver logs detalhados
4. Baixe artefatos com relatórios

### Backup e Recuperação

#### Backup de Configurações

```bash
# Criar backup
tar -czf org-automation-backup-$(date +%Y%m%d).tar.gz \
    config/ .github/ *.py requirements.txt

# Upload para repositório de backup
gh repo create org-automation-backup --private
git remote add backup https://github.com/arturdr-org/org-automation-backup.git
git push backup main
```

#### Recuperação após Falha

```bash
# Reverter para última configuração funcionando
git revert HEAD

# Executar automação em modo de recuperação
DRY_RUN=true RECOVERY_MODE=true python enhanced_automation.py
```

## 🚀 Próximos Passos

Após a configuração inicial:

1. **Execute em DRY-RUN** para validar
2. **Configure alertas** personalizados
3. **Ajuste cronograma** conforme necessário
4. **Monitore relatórios** semanais
5. **Personalize templates** para suas necessidades

## 📞 Suporte

- **Issues**: [arturdr-org/org-automation/issues](https://github.com/arturdr-org/org-automation/issues)
- **Documentação**: Verifique comentários no código
- **Logs**: Sempre disponíveis nos artefatos dos workflows

---

*Configuração completa! O sistema agora está pronto para automatizar e monitorar toda a organização. 🎉*