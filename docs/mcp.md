# 🔗 Model Context Protocol (MCP) Integration

## 📋 Visão Geral

O Model Context Protocol (MCP) é um padrão aberto que permite a comunicação entre aplicações de IA e fontes de dados externas, proporcionando contexto rico e atualizações em tempo real.

## 🏗️ Arquitetura MCP

### Componentes Principais
```
mcp-submodules/
├── github-mcp/           # Integração com GitHub
├── temporal-workflows/   # Workflows Temporal (planejado)
└── nomad-orchestrator/   # Orquestração Nomad (planejado)
```

## 🐙 GitHub MCP

### Localização
`mcp-submodules/github-mcp/`

### Funcionalidades
- **Repository Management**: Criação e configuração de repositórios
- **Issue Tracking**: Gerenciamento de issues e pull requests
- **Workflow Automation**: Integração com GitHub Actions
- **Security Scanning**: Análise de vulnerabilidades

### Configuração
```yaml
github-mcp:
  api_version: "2022-11-28"
  base_url: "https://api.github.com"
  authentication:
    type: "github_app"
    app_id: "${GITHUB_APP_ID}"
    private_key: "${GITHUB_APP_PRIVATE_KEY}"
  
  repositories:
    organization: "arturdr-org"
    include_patterns:
      - "*"
    exclude_patterns:
      - "*.test"
      - "archived-*"
```

### Operações Suportadas
- ✅ `create_repository`: Criação de novos repositórios
- ✅ `apply_labels`: Aplicação de labels padronizadas
- ✅ `setup_branch_protection`: Configuração de proteções
- ✅ `create_issues`: Criação de issues de tracking
- ✅ `generate_reports`: Geração de relatórios

## ⏰ Temporal Workflows MCP (Planejado)

### Objetivo
Integração com Temporal para orquestração de workflows complexos e duradouros.

### Casos de Uso
- Deploys multi-estágio
- Rollbacks automáticos
- Workflows de CI/CD complexos
- Processamento de dados em lote

### Estrutura Planejada
```
temporal-workflows/
├── workflows/
│   ├── deployment.py
│   ├── rollback.py
│   └── data_processing.py
├── activities/
│   ├── github_operations.py
│   ├── notification_activities.py
│   └── validation_activities.py
├── config/
│   └── temporal_config.yaml
└── requirements.txt
```

## 🚀 Nomad Orchestrator MCP (Planejado)

### Objetivo
Integração com HashiCorp Nomad para orquestração de containers e jobs.

### Casos de Uso
- Deploy de aplicações
- Scaling automático
- Health checks
- Service discovery

### Estrutura Planejada
```
nomad-orchestrator/
├── jobs/
│   ├── web_service.nomad
│   ├── background_worker.nomad
│   └── batch_job.nomad
├── policies/
│   ├── deployment.hcl
│   └── scaling.hcl
├── config/
│   └── nomad_config.yaml
└── scripts/
    ├── deploy.py
    └── monitor.py
```

## 🔄 Padrões de Integração

### MCP Client Pattern
```python
from mcp import MCPClient

class GitHubMCPClient(MCPClient):
    def __init__(self, config):
        super().__init__(config)
        self.github_client = self._setup_github_client()
    
    async def execute_operation(self, operation, params):
        # Validação de entrada
        await self._validate_operation(operation, params)
        
        # Execução da operação
        result = await self._execute(operation, params)
        
        # Logging e auditoria
        await self._log_operation(operation, params, result)
        
        return result
```

### Error Handling
```python
class MCPError(Exception):
    """Base exception for MCP operations"""
    pass

class MCPValidationError(MCPError):
    """Validation failed for MCP operation"""
    pass

class MCPExecutionError(MCPError):
    """Execution failed for MCP operation"""
    pass
```

## 📊 Monitoramento MCP

### Métricas Coletadas
- **Operation Latency**: Tempo de execução das operações
- **Success Rate**: Taxa de sucesso por tipo de operação
- **Error Rate**: Taxa de erro por categoria
- **Throughput**: Operações por segundo

### Alertas
- **High Error Rate**: > 5% de falhas em 5 minutos
- **High Latency**: > 10s para operações críticas
- **Service Unavailable**: Falha de conectividade com APIs

## 🔧 Desenvolvimento de Novos MCPs

### Template Base
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseMCP(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize MCP client"""
        pass
    
    @abstractmethod
    async def execute_operation(
        self, 
        operation: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute MCP operation"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup MCP resources"""
        pass
```

### Guidelines
1. **Configuração**: Toda configuração via arquivos YAML
2. **Logging**: Usar logger estruturado
3. **Validação**: Validar todas as entradas
4. **Error Handling**: Tratamento robusto de erros
5. **Testes**: Cobertura mínima de 80%
6. **Documentação**: Documentar todas as operações

## 🧪 Testing MCPs

### Estrutura de Testes
```
tests/mcp/
├── unit/
│   ├── test_github_mcp.py
│   ├── test_temporal_mcp.py
│   └── test_nomad_mcp.py
├── integration/
│   ├── test_github_integration.py
│   └── test_workflow_integration.py
└── fixtures/
    ├── github_responses.json
    └── test_configs.yaml
```

### Mocking Strategy
```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
async def mock_github_client():
    client = AsyncMock()
    client.create_repository.return_value = {"id": 123}
    return client

async def test_create_repository(mock_github_client):
    mcp = GitHubMCP(mock_github_client)
    result = await mcp.create_repository("test-repo")
    assert result["id"] == 123
```

## 🚀 Deployment de MCPs

### Container Strategy
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-m", "mcp.main"]
```

### Configuration Management
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: github-mcp-config
data:
  config.yaml: |
    github:
      api_url: "https://api.github.com"
      organization: "arturdr-org"
      rate_limit: 5000
```

