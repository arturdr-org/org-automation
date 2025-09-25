# 🚀 Guia de Configuração MCP - AI-powered-org-automation-suite v3.0

## 📋 Pré-requisitos

Antes de criar os repositórios MCP, você precisa:

### 1. **Token GitHub com Permissões Adequadas**

Acesse [GitHub Settings → Tokens](https://github.com/settings/tokens) e crie um **Personal Access Token (Classic)** com as seguintes permissões:

#### ✅ **Permissões Obrigatórias:**
- **`repo`** - Full control of private repositories
- **`admin:org`** - Full control of orgs and teams  
- **`workflow`** - Update GitHub Action workflows
- **`project`** - Full control of projects
- **`read:user`** - Read user profile data

#### ⚙️ **Configurações Recomendadas:**
- **Expiration**: 90 days (para segurança)
- **Note**: "AI-powered-org-automation-suite MCP creation - [DATA]"

---

## 🔧 Configuração do Token

### **Opção 1: Variável de Ambiente (Recomendado)**

```bash
# Configure o token como variável de ambiente
export ORG_AUTOMATION_PAT='ghp_seu_token_aqui'

# Verificar se foi configurado
echo "Token configurado: ${ORG_AUTOMATION_PAT:0:10}..."
```

### **Opção 2: Alternativa**

```bash
# Alternativa usando GITHUB_TOKEN
export GITHUB_TOKEN='ghp_seu_token_aqui'
```

### **Opção 3: Arquivo .env (Para desenvolvimento)**

```bash
# Criar arquivo .env na raiz do projeto
echo "ORG_AUTOMATION_PAT=ghp_seu_token_aqui" > .env

# IMPORTANTE: .env já está no .gitignore para segurança
```

---

## 🏗️ Execução da Criação MCP

### **1. Demo/Simulação (Sem Token)**

Para ver como funcionará sem precisar de token:

```bash
cd /home/arturdr/AI-powered-org-automation-suite
python scripts/demo_mcp_creation.py
```

### **2. Execução Real (Com Token)**

Após configurar o token:

```bash
cd /home/arturdr/AI-powered-org-automation-suite
python scripts/create_mcp_repos.py
```

### **3. Validação da Execução**

Verificar se os repositórios foram criados:

```bash
# Listar repositórios da organização
curl -H "Authorization: token $ORG_AUTOMATION_PAT" \
     -H "Accept: application/vnd.github+json" \
     https://api.github.com/orgs/arturdr-org/repos | grep '"name"'
```

---

## 📦 Repositórios que serão Criados

### **1. k8s-argo** 🚀
- **URL**: `https://github.com/arturdr-org/k8s-argo`
- **Descrição**: Kubernetes Argo Workflows - Pipelines robustos
- **Linguagem**: YAML
- **Framework**: Argo Workflows

### **2. n8n-automations** ⚡
- **URL**: `https://github.com/arturdr-org/n8n-automations`
- **Descrição**: n8n Automation Flows - Workflows visuais
- **Linguagem**: JavaScript
- **Framework**: n8n.io

### **3. temporal-workflows** 🛡️
- **URL**: `https://github.com/arturdr-org/temporal-workflows`
- **Descrição**: Temporal Durable Workflows - Execução tolerante a falhas
- **Linguagem**: Python
- **Framework**: Temporal.io

### **4. nomad-orchestrator** 🎯
- **URL**: `https://github.com/arturdr-org/nomad-orchestrator`
- **Descrição**: HashiCorp Nomad Orchestrator - Orquestração leve
- **Linguagem**: HCL
- **Framework**: HashiCorp Nomad

---

## 🏗️ Estrutura Criada em Cada Repositório

### **Arquivos Padrão:**
- `README.md` - Documentação específica do framework
- `.github/workflows/ci-{repo}.yml` - CI/CD especializado
- `Dockerfile` - Para linguagens containerizáveis (Python, JS)

### **Arquivos Específicos por Framework:**

#### **k8s-argo**
```
workflows/example-workflow.yaml    # Argo Workflow exemplo
manifests/                         # Kubernetes manifests
helm/                             # Helm charts (futuro)
```

#### **n8n-automations**
```
workflows/example-automation.json  # n8n workflow exemplo
custom-nodes/                     # Nodes customizados (futuro)
credentials/                      # Templates de credenciais
```

#### **temporal-workflows**
```
workflows/example_workflow.py     # Temporal workflow exemplo
activities/                       # Activities (futuro)
workers/                         # Worker configs (futuro)
```

#### **nomad-orchestrator**
```
jobs/example-job.nomad           # Nomad job exemplo
policies/                        # ACL policies (futuro)
configs/                         # Configuration files (futuro)
```

---

## 🔗 Integração como Submódulos

Após a criação, os repositórios são automaticamente integrados como submódulos:

```bash
# Estrutura resultante
mcp-submodules/
├── k8s-argo/              # Submódulo
├── n8n-automations/       # Submódulo
├── temporal-workflows/    # Submódulo
└── nomad-orchestrator/    # Submódulo
```

### **Comandos de Gerenciamento:**

```bash
# Inicializar submódulos (se necessário)
git submodule update --init --recursive

# Atualizar todos os submódulos
git submodule update --remote

# Atualizar submódulo específico
git submodule update --remote mcp-submodules/k8s-argo
```

---

## 📊 Monitoramento da Execução

### **Logs Detalhados**
O script gera logs detalhados em:
- **Console**: Output em tempo real
- **Arquivo**: `mcp_repos_creation.log`

### **Relatório JSON**
Relatório completo salvo em:
- **Formato**: `mcp_creation_report_YYYYMMDD_HHMMSS.json`
- **Conteúdo**: 
  - Total de repos processados
  - Sucessos e falhas
  - URLs dos repositórios criados
  - Tempo de execução

### **Exemplo de Relatório:**
```json
{
  "total_repos": 4,
  "created_repos": 4,
  "configured_repos": 4,
  "submodules_added": 3,
  "errors": [],
  "processing_time": "23.45s",
  "created_repo_urls": [
    "https://github.com/arturdr-org/k8s-argo",
    "https://github.com/arturdr-org/n8n-automations",
    "https://github.com/arturdr-org/temporal-workflows",
    "https://github.com/arturdr-org/nomad-orchestrator"
  ]
}
```

---

## ⚠️ Troubleshooting

### **Erro: Token não encontrado**
```
ERROR - Token GitHub não encontrado. Configure ORG_AUTOMATION_PAT ou GITHUB_TOKEN
```
**Solução**: Configure o token conforme instruções acima.

### **Erro: Repositório já existe**
```
INFO - Repositório {nome} já existe
```
**Comportamento**: Script pula criação e continua com configuração.

### **Erro: Falha ao adicionar submódulo**
```
WARNING - Submódulo {nome} será adicionado posteriormente
```
**Causa**: Repositório muito novo (ainda inicializando).
**Solução**: Execute novamente após alguns minutos.

### **Erro: Permissões insuficientes**
```
API request failed: 403 - Insufficient permissions
```
**Solução**: Verifique se o token tem todas as permissões necessárias.

---

## 🔄 Próximos Passos

Após execução bem-sucedida:

1. **✅ Verificar Repositórios**: Acessar cada repo criado no GitHub
2. **🔗 Confirmar Submódulos**: `git submodule status`
3. **⚙️ Configurar CI/CD**: Ajustar workflows conforme necessário  
4. **📚 Atualizar Documentação**: Customizar READMEs específicos
5. **🚀 Começar Desenvolvimento**: Implementar workflows nos respectivos repos

---

## 🎯 Comandos Rápidos

```bash
# Setup completo
export ORG_AUTOMATION_PAT='seu_token_aqui'
cd /home/arturdr/AI-powered-org-automation-suite
python scripts/create_mcp_repos.py

# Verificação
git submodule status
git status

# Commit das mudanças
git add .
git commit -m "feat: add MCP repositories as submodules"
git push origin feature/modernize-automation
```

---

**🚀 Pronto para criar o ecossistema MCP mais robusto da organização `arturdr-org`!**