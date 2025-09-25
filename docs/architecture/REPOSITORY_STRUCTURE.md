# 🏗️ Estrutura do Repositório org-automation-suite

Este documento descreve a organização e propósito de cada diretório no repositório.

## 📋 Estrutura Geral

```
org-automation-suite/
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

