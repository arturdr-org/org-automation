#!/bin/bash
# 🏗️ Script para reorganizar estrutura do repositório AI-powered-org-automation-suite
# Implementa as melhores práticas para projetos DevOps/automação

echo "🚀 Iniciando reorganização da estrutura do repositório..."
echo "========================================================"

# ============================================
# 1. Criar estrutura de pastas recomendada
# ============================================

echo "📁 Criando estrutura de pastas..."

# Criar pastas principais se não existirem
mkdir -p core/automation
mkdir -p core/monitoring
mkdir -p core/dashboard
mkdir -p shared/config
mkdir -p shared/utils
mkdir -p shared/templates
mkdir -p logs
mkdir -p docs/architecture
mkdir -p docs/guides
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/e2e

echo "✅ Estrutura de pastas criada"

# ============================================
# 2. Mover arquivos soltos da raiz
# ============================================

echo "📦 Movendo arquivos soltos da raiz..."

# Mover logs para pasta logs/
if [ -f "ai_integration_hub.log" ]; then
    mv -v ai_integration_hub.log logs/
fi

if [ -f "ai_manual_parser.log" ]; then
    mv -v ai_manual_parser.log logs/
fi

if [ -f "mcp_repos_creation.log" ]; then
    mv -v mcp_repos_creation.log logs/
fi

if [ -f "*.log" ]; then
    mv -v *.log logs/ 2>/dev/null || true
fi

# Mover __init__.py para core/
if [ -f "__init__.py" ]; then
    mv -v __init__.py core/
fi

# Mover demo-ai-system.py para scripts/
if [ -f "demo-ai-system.py" ]; then
    mv -v demo-ai-system.py scripts/demo-ai-system.py
fi

# Mover arquivos de relatório JSON para logs/
if [ -f "*.json" ]; then
    mv -v *.json logs/ 2>/dev/null || true
fi

echo "✅ Arquivos da raiz reorganizados"

# ============================================
# 3. Reorganizar documentação
# ============================================

echo "📚 Reorganizando documentação..."

# Mover documentos técnicos para docs/
if [ -f "GITHUB_APP_SETUP.md" ]; then
    mv -v GITHUB_APP_SETUP.md docs/guides/
fi

if [ -f "MODERNIZATION_PLAN.md" ]; then
    mv -v MODERNIZATION_PLAN.md docs/architecture/
fi

# Arquivos que ficam na raiz (governança e setup)
echo "📋 Mantendo na raiz: README.md, GOVERNANCE.md, SETUP.md, LICENSE"

echo "✅ Documentação reorganizada"

# ============================================
# 4. Reorganizar configurações
# ============================================

echo "🔧 Reorganizando configurações..."

# Mover config/ para shared/config/
if [ -d "config" ] && [ "$(ls -A config 2>/dev/null)" ]; then
    cp -r config/* shared/config/ 2>/dev/null || true
    echo "📁 Configurações copiadas para shared/config/"
fi

# Mover common/ para shared/
if [ -d "common" ] && [ "$(ls -A common 2>/dev/null)" ]; then
    cp -r common/* shared/ 2>/dev/null || true
    echo "📁 Utilitários comuns movidos para shared/"
fi

echo "✅ Configurações reorganizadas"

# ============================================
# 5. Reorganizar submódulos MCP
# ============================================

echo "🔗 Reorganizando submódulos MCP..."

# Mover github-mcp para mcp-submodules/
if [ -d "github-mcp" ]; then
    if [ ! -d "mcp-submodules/github-mcp" ]; then
        mv -v github-mcp mcp-submodules/
    else
        echo "⚠️  mcp-submodules/github-mcp já existe, mantendo atual"
    fi
fi

echo "✅ Submódulos MCP reorganizados"

# ============================================
# 6. Atualizar .gitignore
# ============================================

echo "🚫 Atualizando .gitignore..."

cat >> .gitignore << 'EOF'

# ============================================
# Logs e arquivos temporários
# ============================================
logs/*.log
*.log
*.tmp
*.temp
.DS_Store
Thumbs.db

# ============================================
# Arquivos de configuração sensíveis
# ============================================
shared/config/secrets.json
shared/config/api-keys.json
.env.local
.env.production

# ============================================
# Cache e arquivos gerados
# ============================================
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# ============================================
# IDEs
# ============================================
.vscode/settings.json
.idea/
*.swp
*.swo
*~

# ============================================
# Arquivos específicos do projeto
# ============================================
ai_knowledge_base.json
mcp_creation_demo_report_*.json
backup_pre_migration/

EOF

echo "✅ .gitignore atualizado"

# ============================================
# 7. Criar arquivo de documentação da arquitetura
# ============================================

echo "📖 Criando documentação da arquitetura..."

cat > docs/architecture/REPOSITORY_STRUCTURE.md << 'EOF'
# 🏗️ Estrutura do Repositório AI-powered-org-automation-suite

Este documento descreve a organização e propósito de cada diretório no repositório.

## 📋 Estrutura Geral

```
AI-powered-org-automation-suite/
├── 🧠 core/                     # Sistema central de automação
├── 🔧 modules/                  # Funcionalidades e integrações
├── 🤝 shared/                   # Recursos compartilhados
├── 🔗 mcp-submodules/           # Submódulos MCP
├── 🧪 tests/                    # Testes automatizados
├── 📜 scripts/                  # Scripts auxiliares
├── 📚 docs/                     # Documentação técnica
├── 📊 logs/                     # Logs de execução
├── ⚙️ .github/                  # Configuração GitHub Actions
├── 📄 README.md                 # Visão geral do projeto
├── 📋 GOVERNANCE.md             # Governança e contribuição
├── 🛠️ SETUP.md                  # Guia de instalação
├── 📦 requirements.txt          # Dependências Python
├── 🔧 setup.py                  # Configuração do pacote
└── 🚫 .gitignore                # Arquivos ignorados

```

## 📁 Detalhamento dos Diretórios

### 🧠 core/
**Sistema central de automação**
- `automation/` - Lógica principal de automação
- `monitoring/` - Monitoramento e métricas
- `dashboard/` - Interface de visualização

### 🔧 modules/
**Funcionalidades específicas e integrações**
- `security/` - Módulos de segurança
- `cicd/` - Integração contínua
- `notifications/` - Sistema de notificações
- `quality/` - Controle de qualidade

### 🤝 shared/
**Recursos compartilhados entre módulos**
- `config/` - Configurações globais
- `utils/` - Utilitários comuns
- `templates/` - Templates reutilizáveis

### 🔗 mcp-submodules/
**Submódulos Model Context Protocol**
- `github-mcp/` - Integração GitHub via MCP
- Outros submódulos MCP conforme necessário

### 🧪 tests/
**Testes automatizados**
- `unit/` - Testes unitários
- `integration/` - Testes de integração
- `e2e/` - Testes end-to-end

### 📜 scripts/
**Scripts auxiliares e utilitários**
- Scripts de setup, backup, manutenção
- Scripts de demonstração e troubleshooting

### 📚 docs/
**Documentação técnica**
- `architecture/` - Arquitetura e design
- `guides/` - Guias de uso e configuração

### 📊 logs/
**Logs de execução e debugging**
- Logs separados por componente
- Rotação automática (via .gitignore)

## 🎯 Princípios de Organização

1. **Separação de Responsabilidades**: Cada diretório tem um propósito claro
2. **Escalabilidade**: Estrutura suporta crescimento do projeto
3. **Manutenibilidade**: Fácil navegação e localização de código
4. **Padrões**: Seguimento de convenções da comunidade Python/DevOps

## 🔄 Imports e Referências

```python
# Imports do core
from core.automation import AutomationEngine
from core.monitoring import MetricsCollector

# Imports de módulos
from modules.security import SecurityValidator
from modules.notifications import NotificationManager

# Imports compartilhados
from shared.utils import ConfigLoader
from shared.config import settings
```

## 📈 Evolução da Estrutura

Esta estrutura foi criada para:
- ✅ Melhorar organização e clareza
- ✅ Facilitar colaboração em equipe
- ✅ Seguir melhores práticas DevOps
- ✅ Suportar crescimento do projeto
- ✅ Manter compatibilidade com ferramentas

EOF

echo "✅ Documentação da arquitetura criada"

# ============================================
# 8. Remover pastas antigas vazias (se aplicável)
# ============================================

echo "🧹 Limpando pastas vazias..."

# Remover config/ original se vazio
if [ -d "config" ] && [ ! "$(ls -A config 2>/dev/null)" ]; then
    rmdir config
    echo "📁 Pasta config/ vazia removida"
fi

# Remover common/ original se vazio  
if [ -d "common" ] && [ ! "$(ls -A common 2>/dev/null)" ]; then
    rmdir common
    echo "📁 Pasta common/ vazia removida"
fi

echo "✅ Limpeza concluída"

# ============================================
# 9. Resumo final
# ============================================

echo ""
echo "🎉 REORGANIZAÇÃO CONCLUÍDA!"
echo "=============================="
echo ""
echo "📊 Estrutura final:"
find . -type d -name ".git" -prune -o -type d -print | head -20
echo ""
echo "📋 Próximos passos:"
echo "1. ✅ Verifique se todos os arquivos foram movidos corretamente"
echo "2. ✅ Atualize imports nos arquivos Python se necessário" 
echo "3. ✅ Teste se os scripts ainda funcionam"
echo "4. ✅ Faça commit das mudanças"
echo ""
echo "📚 Documentação: docs/architecture/REPOSITORY_STRUCTURE.md"
echo "🚀 Repositório organizado e pronto para colaboração!"