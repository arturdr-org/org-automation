#!/usr/bin/env python3
"""
🏗️ MCP Repository Creator - org-automation v3.0

Script para criar e configurar repositórios MCP específicos:
- k8s-argo: Pipelines Kubernetes com Argo Workflows
- n8n-automations: Flows automatizados via n8n.io
- temporal-workflows: Workflows robustos com Temporal.io
- nomad-orchestrator: Orquestração leve via HashiCorp Nomad

Baseado nas melhores práticas de Multi-Cloud Platform (MCP)
e integração com org-automation-suite.
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import yaml

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_repos_creation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MCPRepositoryCreator:
    """Criador de repositórios MCP específicos."""
    
    def __init__(self):
        """Inicializar criador de repositórios MCP."""
        self.org_name = os.getenv('ORG_NAME', 'arturdr-org')
        self.github_token = self._get_github_token()
        self.root_dir = Path(__file__).parent.parent
        
        # URLs da API GitHub
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Definições dos repositórios MCP
        self.mcp_repos = {
            'k8s-argo': {
                'description': '🚀 Kubernetes Argo Workflows - Pipelines de automação robustos e escaláveis',
                'topics': ['kubernetes', 'argo-workflows', 'ci-cd', 'automation', 'devops'],
                'language': 'yaml',
                'framework': 'Argo Workflows'
            },
            'n8n-automations': {
                'description': '⚡ n8n Automation Flows - Workflows visuais e integração de APIs',
                'topics': ['n8n', 'automation', 'workflow', 'api-integration', 'low-code'],
                'language': 'javascript',
                'framework': 'n8n.io'
            },
            'temporal-workflows': {
                'description': '🛡️ Temporal Durable Workflows - Execução durável e tolerante a falhas',
                'topics': ['temporal', 'workflows', 'reliability', 'microservices', 'distributed-systems'],
                'language': 'python',
                'framework': 'Temporal.io'
            },
            'nomad-orchestrator': {
                'description': '🎯 HashiCorp Nomad Orchestrator - Orquestração leve e flexível',
                'topics': ['nomad', 'orchestration', 'hashicorp', 'containers', 'scheduling'],
                'language': 'hcl',
                'framework': 'HashiCorp Nomad'
            }
        }
        
        logger.info(f"🏗️ MCP Repository Creator iniciado para {self.org_name}")
    
    def _get_github_token(self) -> str:
        """Obter token GitHub com fallback."""
        token = (
            os.getenv('ORG_AUTOMATION_PAT') or 
            os.getenv('GITHUB_TOKEN')
        )
        if not token:
            raise ValueError("Token GitHub não encontrado. Configure ORG_AUTOMATION_PAT ou GITHUB_TOKEN")
        return token
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
        """Fazer requisição para API GitHub com tratamento de erro."""
        url = f"{self.api_base}/{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            if response.status_code in [200, 201, 204]:
                return response.json() if response.content else {}
            else:
                logger.warning(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {e}")
            return None
    
    def create_repository(self, repo_name: str, config: Dict[str, Any]) -> bool:
        """Criar repositório no GitHub."""
        logger.info(f"📦 Criando repositório {repo_name}...")
        
        # Verificar se repositório já existe
        endpoint = f"repos/{self.org_name}/{repo_name}"
        existing = self._make_request(endpoint)
        
        if existing:
            logger.info(f"  ℹ️ Repositório {repo_name} já existe")
            return True
        
        # Dados para criação do repositório
        repo_data = {
            "name": repo_name,
            "description": config['description'],
            "private": False,
            "has_issues": True,
            "has_projects": True,
            "has_wiki": True,
            "has_downloads": True,
            "auto_init": True,
            "license_template": "mit",
            "gitignore_template": config['language'],
            "allow_squash_merge": True,
            "allow_merge_commit": True,
            "allow_rebase_merge": True,
            "delete_branch_on_merge": True,
            "vulnerability_alerts_enabled": True,
            "automated_security_fixes_enabled": True
        }
        
        # Criar repositório na organização
        endpoint = f"orgs/{self.org_name}/repos"
        response = self._make_request(endpoint, method='POST', data=repo_data)
        
        if response:
            logger.info(f"  ✅ Repositório {repo_name} criado com sucesso")
            
            # Configurar topics
            self._set_repository_topics(repo_name, config['topics'])
            
            return True
        else:
            logger.error(f"  ❌ Falha ao criar repositório {repo_name}")
            return False
    
    def _set_repository_topics(self, repo_name: str, topics: List[str]) -> bool:
        """Configurar topics do repositório."""
        endpoint = f"repos/{self.org_name}/{repo_name}/topics"
        topics_data = {"names": topics}
        
        response = self._make_request(endpoint, method='PUT', data=topics_data)
        
        if response:
            logger.info(f"    🏷️ Topics configurados: {', '.join(topics)}")
            return True
        else:
            logger.warning(f"    ⚠️ Falha ao configurar topics para {repo_name}")
            return False
    
    def create_initial_structure(self, repo_name: str, config: Dict[str, Any]) -> bool:
        """Criar estrutura inicial do repositório MCP."""
        logger.info(f"🏗️ Criando estrutura inicial para {repo_name}...")
        
        # README específico para cada MCP
        readme_content = self._generate_mcp_readme(repo_name, config)
        self._create_file_in_repo(repo_name, "README.md", readme_content)
        
        # Dockerfile se aplicável
        if config['language'] in ['python', 'javascript']:
            dockerfile_content = self._generate_dockerfile(config['language'])
            self._create_file_in_repo(repo_name, "Dockerfile", dockerfile_content)
        
        # Workflow de CI/CD específico
        workflow_content = self._generate_mcp_workflow(repo_name, config)
        self._create_file_in_repo(repo_name, f".github/workflows/ci-{repo_name}.yml", workflow_content)
        
        # Arquivo de configuração específico
        if repo_name == 'k8s-argo':
            config_content = self._generate_argo_config()
            self._create_file_in_repo(repo_name, "workflows/example-workflow.yaml", config_content)
        elif repo_name == 'n8n-automations':
            config_content = self._generate_n8n_config()
            self._create_file_in_repo(repo_name, "workflows/example-automation.json", config_content)
        elif repo_name == 'temporal-workflows':
            config_content = self._generate_temporal_config()
            self._create_file_in_repo(repo_name, "workflows/example_workflow.py", config_content)
        elif repo_name == 'nomad-orchestrator':
            config_content = self._generate_nomad_config()
            self._create_file_in_repo(repo_name, "jobs/example-job.nomad", config_content)
        
        logger.info(f"  ✅ Estrutura inicial criada para {repo_name}")
        return True
    
    def _create_file_in_repo(self, repo_name: str, file_path: str, content: str) -> bool:
        """Criar arquivo no repositório."""
        import base64
        
        # Verificar se arquivo já existe
        endpoint = f"repos/{self.org_name}/{repo_name}/contents/{file_path}"
        existing = self._make_request(endpoint)
        
        if existing:
            logger.info(f"    ℹ️ Arquivo {file_path} já existe em {repo_name}")
            return False
        
        # Criar arquivo
        create_data = {
            "message": f"feat: add {file_path}",
            "content": base64.b64encode(content.encode()).decode(),
            "branch": "main"
        }
        
        response = self._make_request(endpoint, method='PUT', data=create_data)
        
        if response:
            logger.info(f"    ✅ Arquivo {file_path} criado em {repo_name}")
            return True
        else:
            logger.error(f"    ❌ Falha ao criar arquivo {file_path} em {repo_name}")
            return False
    
    def _generate_mcp_readme(self, repo_name: str, config: Dict[str, Any]) -> str:
        """Gerar README específico para MCP."""
        framework = config['framework']
        
        return f"""# {repo_name}

{config['description']}

## 🎯 Visão Geral

Este repositório contém {framework} workflows e configurações para automação organizacional da `{self.org_name}`.

## 🏗️ Arquitetura

### Integração com org-automation-suite

Este repositório é parte da arquitetura modular MCP (Multi-Cloud Platform):

```
org-automation-suite/
├── core/                    # Sistema central
├── modules/                 # Módulos específicos
├── common/                  # Recursos compartilhados
└── mcp-submodules/         # Submódulos MCP
    └── {repo_name}/        # Este repositório
```

### Comunicação

- **APIs REST**: Endpoints para integração
- **Webhooks**: Eventos automáticos
- **GitHub Actions**: Workflows cross-repo

## 🚀 Como Usar

### Pré-requisitos

- {framework} instalado
- Acesso à organização `{self.org_name}`
- Configuração de secrets apropriada

### Instalação

```bash
git clone https://github.com/{self.org_name}/{repo_name}.git
cd {repo_name}
# Comandos específicos do framework
```

### Configuração

1. Configure as variáveis de ambiente necessárias
2. Ajuste os arquivos de configuração específicos
3. Execute os workflows de exemplo

## 📊 Monitoramento

Este repositório integra com:

- **Monitoring**: Métricas e observabilidade
- **Alerting**: Notificações de falhas
- **Logging**: Registro de execuções

## 🤝 Contribuição

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para guidelines de contribuição.

## 📝 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🔗 Links Relacionados

- [org-automation-suite](https://github.com/{self.org_name}/org-automation)
- [Documentação {framework}](#{framework.lower().replace(' ', '-')})
- [Documentação da Arquitetura MCP](https://github.com/{self.org_name}/org-automation/blob/main/docs/MCP_ARCHITECTURE.md)

---

**Parte da família org-automation v3.0** 🚀
"""
    
    def _generate_dockerfile(self, language: str) -> str:
        """Gerar Dockerfile baseado na linguagem."""
        if language == 'python':
            return """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
"""
        elif language == 'javascript':
            return """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

CMD ["npm", "start"]
"""
        else:
            return "# Dockerfile específico será adicionado conforme necessário\n"
    
    def _generate_mcp_workflow(self, repo_name: str, config: Dict[str, Any]) -> str:
        """Gerar workflow de CI/CD específico para MCP."""
        return f"""name: "🚀 {repo_name.title()} CI/CD"

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

env:
  FRAMEWORK: {config['framework']}

jobs:
  test:
    name: "🧪 Test & Validate"
    runs-on: ubuntu-latest
    
    steps:
    - name: "📥 Checkout Code"
      uses: actions/checkout@v4
    
    - name: "⚙️ Setup Environment"
      run: |
        echo "🔧 Setting up {config['framework']} environment..."
        # Comandos específicos do framework
    
    - name: "🔍 Lint & Validate"
      run: |
        echo "🔍 Validating {config['framework']} configurations..."
        # Validação específica
    
    - name: "🧪 Run Tests"
      run: |
        echo "🧪 Running {config['framework']} tests..."
        # Testes específicos

  deploy:
    name: "🚀 Deploy"
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: "📥 Checkout Code"
      uses: actions/checkout@v4
    
    - name: "🚀 Deploy to Environment"
      run: |
        echo "🚀 Deploying {config['framework']} workflows..."
        # Deploy específico

  notify:
    name: "📢 Notify org-automation-suite"
    runs-on: ubuntu-latest
    needs: [test, deploy]
    if: always()
    
    steps:
    - name: "📤 Send Update to Main Repo"
      run: |
        curl -X POST \\
          -H "Authorization: token ${{{{ secrets.GITHUB_TOKEN }}}}" \\
          -H "Accept: application/vnd.github+json" \\
          "https://api.github.com/repos/{self.org_name}/org-automation/dispatches" \\
          -d '{{"event_type": "mcp-update", "client_payload": {{"repo": "{repo_name}", "status": "${{{{ job.status }}}}"}}}}'
"""
    
    def _generate_argo_config(self) -> str:
        """Gerar configuração exemplo para Argo Workflows."""
        return """apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: org-automation-example-
spec:
  entrypoint: main
  templates:
  - name: main
    steps:
    - - name: validate
        template: validate-config
    - - name: deploy
        template: deploy-automation
  
  - name: validate-config
    container:
      image: alpine:latest
      command: [sh, -c]
      args: ["echo 'Validating org-automation configuration...'"]
  
  - name: deploy-automation
    container:
      image: alpine:latest
      command: [sh, -c]
      args: ["echo 'Deploying automation workflows...'"]
"""
    
    def _generate_n8n_config(self) -> str:
        """Gerar configuração exemplo para n8n."""
        return """{
  "name": "org-automation-example",
  "nodes": [
    {
      "parameters": {},
      "id": "start-node",
      "name": "Start",
      "type": "n8n-nodes-base.start",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "url": "https://api.github.com/repos/arturdr-org/AI-powered-org-automation-suite",
        "options": {}
      },
      "id": "github-node",
      "name": "GitHub",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [460, 300]
    }
  ],
  "connections": {
    "Start": {
      "main": [
        [
          {
            "node": "GitHub",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}"""
    
    def _generate_temporal_config(self) -> str:
        """Gerar configuração exemplo para Temporal."""
        return '''"""
Exemplo de Workflow Temporal para org-automation
"""

import asyncio
from datetime import timedelta
from temporalio import workflow
from temporalio.client import Client


@workflow.defn
class OrgAutomationWorkflow:
    """Workflow de automação organizacional."""
    
    @workflow.run
    async def run(self, org_name: str) -> str:
        """Executar automação organizacional."""
        
        # Atividade: Sincronizar repositórios
        await workflow.execute_activity(
            sync_repositories,
            org_name,
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        # Atividade: Aplicar políticas
        await workflow.execute_activity(
            apply_policies,
            org_name,
            start_to_close_timeout=timedelta(minutes=10)
        )
        
        # Atividade: Gerar relatório
        report = await workflow.execute_activity(
            generate_report,
            org_name,
            start_to_close_timeout=timedelta(minutes=2)
        )
        
        return f"Automação completa para {org_name}: {report}"


@workflow.defn
async def sync_repositories(org_name: str) -> str:
    """Sincronizar repositórios da organização."""
    # Implementar lógica de sincronização
    return f"Repositórios sincronizados para {org_name}"


@workflow.defn
async def apply_policies(org_name: str) -> str:
    """Aplicar políticas organizacionais."""
    # Implementar aplicação de políticas
    return f"Políticas aplicadas para {org_name}"


@workflow.defn
async def generate_report(org_name: str) -> str:
    """Gerar relatório de automação."""
    # Implementar geração de relatório
    return f"Relatório gerado para {org_name}"
'''
    
    def _generate_nomad_config(self) -> str:
        """Gerar configuração exemplo para Nomad."""
        return '''job "org-automation" {
  datacenters = ["dc1"]
  type = "batch"

  group "automation" {
    count = 1

    task "run-automation" {
      driver = "docker"

      config {
        image = "python:3.9-slim"
        command = "python"
        args = ["/app/automation.py"]
        
        volumes = [
          "local:/app"
        ]
      }

      template {
        data = <<EOF
#!/usr/bin/env python3
"""
Org Automation via Nomad
"""
import os
import logging

def main():
    logging.info("🚀 Starting org-automation via Nomad...")
    
    # Implementar lógica de automação
    org_name = os.getenv("ORG_NAME", "arturdr-org")
    logging.info(f"Processing organization: {org_name}")
    
    logging.info("✅ Automation completed successfully!")

if __name__ == "__main__":
    main()
EOF
        destination = "local/automation.py"
      }

      resources {
        cpu    = 100
        memory = 256
      }

      env {
        ORG_NAME = "arturdr-org"
      }
    }
  }
}'''
    
    def create_submodule_integration(self, repo_name: str) -> bool:
        """Criar integração como submódulo no repositório principal."""
        logger.info(f"🔗 Integrando {repo_name} como submódulo...")
        
        try:
            # Navegar para pasta mcp-submodules
            submodules_dir = self.root_dir / "mcp-submodules"
            
            # Adicionar como submódulo
            subprocess.run([
                "git", "submodule", "add", 
                f"https://github.com/{self.org_name}/{repo_name}.git",
                str(submodules_dir / repo_name)
            ], check=True, cwd=self.root_dir)
            
            logger.info(f"  ✅ Submódulo {repo_name} adicionado")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"  ❌ Erro ao adicionar submódulo {repo_name}: {e}")
            return False
    
    def run_mcp_creation(self) -> Dict[str, Any]:
        """Executar criação completa dos repositórios MCP."""
        logger.info("🏗️ Iniciando criação dos repositórios MCP...")
        
        start_time = datetime.now()
        
        results = {
            "total_repos": len(self.mcp_repos),
            "created_repos": 0,
            "configured_repos": 0,
            "submodules_added": 0,
            "errors": [],
            "processing_time": None,
            "created_repo_urls": []
        }
        
        # Criar cada repositório MCP
        for repo_name, config in self.mcp_repos.items():
            logger.info(f"📦 Processando repositório MCP: {repo_name}")
            
            try:
                # Criar repositório
                if self.create_repository(repo_name, config):
                    results['created_repos'] += 1
                    results['created_repo_urls'].append(f"https://github.com/{self.org_name}/{repo_name}")
                    
                    # Aguardar um pouco para o repositório ser inicializado
                    import time
                    time.sleep(2)
                    
                    # Criar estrutura inicial
                    if self.create_initial_structure(repo_name, config):
                        results['configured_repos'] += 1
                    
                    # Adicionar como submódulo (opcional - pode falhar se repo não estiver pronto)
                    try:
                        if self.create_submodule_integration(repo_name):
                            results['submodules_added'] += 1
                    except Exception as e:
                        logger.warning(f"  ⚠️ Submódulo {repo_name} será adicionado posteriormente: {e}")
                
            except Exception as e:
                error_msg = f"Erro ao processar {repo_name}: {str(e)}"
                logger.error(f"  ❌ {error_msg}")
                results['errors'].append(error_msg)
        
        # Calcular tempo de processamento
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        results['processing_time'] = f"{processing_time:.2f}s"
        
        # Relatório final
        logger.info("\n" + "="*60)
        logger.info("🎉 CRIAÇÃO DE REPOSITÓRIOS MCP CONCLUÍDA!")
        logger.info("="*60)
        logger.info(f"📊 Repositórios criados: {results['created_repos']}/{results['total_repos']}")
        logger.info(f"⚙️ Repositórios configurados: {results['configured_repos']}")
        logger.info(f"🔗 Submódulos adicionados: {results['submodules_added']}")
        logger.info(f"⏱️ Tempo total: {results['processing_time']}")
        
        if results['created_repo_urls']:
            logger.info("\n🔗 Repositórios MCP criados:")
            for url in results['created_repo_urls']:
                logger.info(f"  • {url}")
        
        if results['errors']:
            logger.warning(f"\n⚠️ Erros encontrados: {len(results['errors'])}")
            for error in results['errors']:
                logger.warning(f"  • {error}")
        
        # Salvar relatório
        report_file = self.root_dir / f"mcp_creation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"\n📄 Relatório salvo em: {report_file}")
        
        return results


def main():
    """Função principal."""
    try:
        creator = MCPRepositoryCreator()
        results = creator.run_mcp_creation()
        
        # Código de saída baseado no sucesso
        if results.get('errors'):
            sys.exit(1)  # Houve erros
        else:
            sys.exit(0)  # Sucesso completo
            
    except Exception as e:
        logger.error(f"❌ Erro fatal na criação MCP: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()