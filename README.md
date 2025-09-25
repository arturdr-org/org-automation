# 🤖 Automação da Organização arturdr-org

> Sistema completo de padronização e automação para todos os repositórios da organização `arturdr-org`.

## 📋 Visão Geral

Este repositório contém o sistema central de automação da organização `arturdr-org`, projetado para:

- 🏷️ **Padronizar labels** em todos os repositórios
- 📄 **Aplicar templates** uniformes para issues e PRs
- 🔒 **Configurar proteções** de branch automaticamente
- 📊 **Monitorar conformidade** e gerar relatórios
- 🔄 **Executar automações** de forma periódica e confiável

## 🏗️ Arquitetura

### 📁 Estrutura do Projeto

```
org-automation-suite/
├── 📁 config/                          # Configurações centralizadas
│   ├── labels.yml                      # Definição de labels padrão
│   ├── branch_protection.yml           # Regras de proteção de branches
│   ├── CODEOWNERS                     # Template padrão de CODEOWNERS
│   └── 📁 templates/                   # Templates para issues e PRs
│       ├── bug_report.md
│       ├── feature_request.md
│       └── pull_request_template.md
├── 📁 .github/workflows/              # Workflows de automação
│   ├── enhanced-automation.yml        # Automação principal
│   └── health-monitoring.yml          # Monitoramento e alertas
├── enhanced_automation.py             # Script principal de automação
├── monitoring.py                      # Sistema de monitoramento
├── automa_org.py                      # Script legado (compatibilidade)
└── requirements.txt                   # Dependências Python
```

## 🚀 Funcionalidades

### 🎯 Automação Principal

- **Aplicação de Labels**: Aplica labels padrão e personalizadas da organização
- **Templates de Issues/PRs**: Cria templates padronizados para melhor colaboração
- **Arquivo CODEOWNERS**: Define proprietários de código automaticamente
- **Proteções de Branch**: Aplica regras de proteção nos branches principais
- **Issues de Checklist**: Cria issues de rastreamento para cada repositório
- **Relatórios Detalhados**: Gera relatórios completos de cada execução

### 🏥 Sistema de Monitoramento

- **Health Checks**: Verifica a conformidade de todos os repositórios
- **Alertas Automáticos**: Cria issues quando problemas críticos são detectados
- **Relatórios Semanais**: Gera relatórios periódicos de saúde da organização
- **Métricas de Conformidade**: Acompanha taxas de conformidade ao longo do tempo

## ⚙️ Configuração

### 🔑 Autenticação

O sistema suporta dois métodos de autenticação:

1. **GitHub App (Recomendado)**:
   ```bash
   ORG_APP_ID="your_app_id"
   ORG_APP_PRIVATE_KEY="your_private_key"
   ```

2. **Personal Access Token**:
   ```bash
   ORG_AUTOMATION_PAT="your_token"
   ```

### 🏷️ Configuração de Labels

Edite `config/labels.yml` para definir labels padrão:

```yaml
default_labels:
  - name: "bug"
    color: "d73a4a"
    description: "Algo não está funcionando"

org_labels:
  - name: "priority:high"
    color: "d93f0b"
    description: "Alta prioridade"
```

### 🔒 Proteções de Branch

Configure regras em `config/branch_protection.yml`:

```yaml
branch_protection:
  main:
    required_pull_request_reviews:
      required_approving_review_count: 1
    enforce_admins: false
    allow_force_pushes: false
```

## 🎮 Como Usar

### 💻 Execução Local

```bash
# 1. Clonar e configurar ambiente
git clone https://github.com/arturdr-org/org-automation-suite.git
cd org-automation-suite
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configurar token
export ORG_AUTOMATION_PAT="seu_token_aqui"

# 3. Executar automação (modo DRY-RUN)
DRY_RUN=true python enhanced_automation.py

# 4. Executar em produção
python enhanced_automation.py

# 5. Executar monitoramento
python monitoring.py
```

### ☁️ Execução via GitHub Actions

#### Automação Manual
1. Vá para **Actions** → **🚀 Enhanced Organization Automation**
2. Clique em **Run workflow**
3. Configure opções:
   - **DRY-RUN**: `true` para teste, `false` para produção
   - **Repositórios específicos**: deixe vazio para todos

#### Automação Programada
- **Execução automática**: Diariamente às 2:00 UTC
- **Health Check**: Duas vezes por dia (6:00 e 18:00 UTC)
- **Relatório semanal**: Segundas-feiras às 6:00 UTC

## 📊 Monitoramento e Relatórios

### 🏥 Health Check

O sistema monitora automaticamente:
- ✅ Conformidade de labels
- 📄 Presença de templates
- 🔒 Proteções de branch
- 🔄 Saúde dos workflows

### 📈 Métricas

- **Taxa de Conformidade**: % de repositórios em conformidade
- **Status da Automação**: Healthy, Warning, ou Critical
- **Tempo de Execução**: Duração das automações
- **Taxa de Sucesso**: % de execuções bem-sucedidas

### 🚨 Alertas

Alertas automáticos são criados quando:
- Taxa de conformidade < 60%
- Falhas frequentes nos workflows
- Problemas críticos detectados

## 🔧 Personalização

### 🏷️ Adicionando Novas Labels

1. Edite `config/labels.yml`
2. Adicione a label na seção apropriada:
   ```yaml
   org_labels:
     - name: "nova-label"
       color: "ff0000"
       description: "Descrição da nova label"
   ```
3. Faça commit e push - a automação aplicará automaticamente

### 📄 Criando Novos Templates

1. Adicione arquivo em `config/templates/`
2. Configure em `enhanced_automation.py`:
   ```python
   templates.append({
       "path": ".github/ISSUE_TEMPLATE/custom.md",
       "source": TEMPLATES_DIR / "custom.md",
       "message": "chore: add custom template"
   })
   ```

### 🔒 Configurando Novas Proteções

1. Edite `config/branch_protection.yml`
2. Adicione regras para novos padrões de branches
3. Teste com DRY-RUN primeiro

## 🛠️ Desenvolvimento

### 🧪 Modo de Desenvolvimento

```bash
# Sempre use DRY-RUN durante desenvolvimento
DRY_RUN=true python enhanced_automation.py

# Teste monitoramento
python monitoring.py

# Validar configurações
yaml-lint config/*.yml
```

### 🧪 Testes

```bash
# Executar testes básicos
python -c "import enhanced_automation; print('✅ Script carregado com sucesso')"

# Validar configurações YAML
python -c "import yaml; yaml.safe_load(open('config/labels.yml')); print('✅ YAML válido')"
```

## 📚 Recursos Adicionais

### 🔗 Links Úteis

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [GitHub Apps Documentation](https://docs.github.com/en/developers/apps)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)

### 📞 Suporte

- **Issues**: Use as issues deste repositório
- **Discussões**: Para ideias e propostas
- **Documentação**: Verifique os workflows e comentários no código

## 🔄 Changelog

- **v2.0.0** - Sistema completo com monitoramento e configurações centralizadas
- **v1.0.0** - Sistema básico de automação

---

*Este sistema foi desenvolvido para manter a consistência e qualidade em todos os repositórios da organização `arturdr-org`.*
