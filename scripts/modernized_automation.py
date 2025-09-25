#!/usr/bin/env python3
"""
🚀 Modernized Organization Automation - AI-powered-org-automation-suite v3.0

Sistema de automação organizacional modernizado com integração das melhores 
práticas e ferramentas do ecossistema GitHub.

Substitui scripts customizados por soluções nativas sempre que possível,
mantendo compatibilidade com funcionalidades existentes.
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
        logging.FileHandler('modernized_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ModernizedOrganizationAutomation:
    """Sistema de automação organizacional modernizado."""
    
    def __init__(self):
        """Inicializar sistema de automação modernizado."""
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
        
        # Configurações modernizadas
        self.modern_tools = {
            'dependabot': True,
            'codeql': True,
            'sonarcloud': True,
            'snyk': True,
            'codecov': True,
            'stale_bot': True
        }
        
        logger.info(f"🚀 Modernized Automation iniciado para {self.org_name}")
    
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
    
    def get_organization_repos(self) -> List[Dict]:
        """Obter repositórios da organização."""
        logger.info("📊 Obtendo repositórios da organização...")
        
        repos = []
        page = 1
        per_page = 100
        
        while True:
            endpoint = f"orgs/{self.org_name}/repos?page={page}&per_page={per_page}"
            response = self._make_request(endpoint)
            
            if not response:
                break
                
            if not response:  # Lista vazia
                break
                
            repos.extend(response)
            
            if len(response) < per_page:
                break
                
            page += 1
        
        logger.info(f"✅ Encontrados {len(repos)} repositórios")
        return repos
    
    def check_modern_tools_status(self, repo: Dict) -> Dict[str, bool]:
        """Verificar status das ferramentas modernas em um repositório."""
        repo_name = repo['name']
        status = {}
        
        # Verificar Dependabot
        endpoint = f"repos/{self.org_name}/{repo_name}/vulnerability-alerts"
        dependabot_response = self._make_request(endpoint)
        status['dependabot'] = dependabot_response is not None
        
        # Verificar CodeQL (GitHub Advanced Security)
        endpoint = f"repos/{self.org_name}/{repo_name}/code-scanning/alerts"
        codeql_response = self._make_request(endpoint)
        status['codeql'] = codeql_response is not None
        
        # Verificar se tem workflow de CI/CD moderno
        endpoint = f"repos/{self.org_name}/{repo_name}/actions/workflows"
        workflows_response = self._make_request(endpoint)
        has_modern_ci = False
        if workflows_response and 'workflows' in workflows_response:
            workflow_names = [w['name'].lower() for w in workflows_response['workflows']]
            has_modern_ci = any('ci' in name or 'build' in name or 'test' in name for name in workflow_names)
        status['modern_ci'] = has_modern_ci
        
        # Verificar branch protection
        endpoint = f"repos/{self.org_name}/{repo_name}/branches/main/protection"
        protection_response = self._make_request(endpoint)
        status['branch_protection'] = protection_response is not None
        
        return status
    
    def enable_dependabot(self, repo: Dict) -> bool:
        """Ativar Dependabot em um repositório (via arquivo de configuração)."""
        repo_name = repo['name']
        logger.info(f"🤖 Configurando Dependabot para {repo_name}...")
        
        # Verificar se já existe configuração
        endpoint = f"repos/{self.org_name}/{repo_name}/contents/.github/dependabot.yml"
        existing_config = self._make_request(endpoint)
        
        if existing_config:
            logger.info(f"  ℹ️ Dependabot já configurado em {repo_name}")
            return True
        
        # Criar configuração padrão baseada na linguagem do repo
        dependabot_config = self._generate_dependabot_config(repo)
        
        # Criar arquivo dependabot.yml
        create_data = {
            "message": "feat: add Dependabot configuration for automated dependency updates",
            "content": dependabot_config,
            "branch": "main"
        }
        
        create_response = self._make_request(endpoint, method='PUT', data=create_data)
        
        if create_response:
            logger.info(f"  ✅ Dependabot configurado em {repo_name}")
            return True
        else:
            logger.error(f"  ❌ Falha ao configurar Dependabot em {repo_name}")
            return False
    
    def _generate_dependabot_config(self, repo: Dict) -> str:
        """Gerar configuração do Dependabot baseada na linguagem do repositório."""
        import base64
        
        language = repo.get('language', '').lower()
        
        config = {
            'version': 2,
            'updates': []
        }
        
        # Configuração baseada na linguagem
        if language == 'python':
            config['updates'].append({
                'package-ecosystem': 'pip',
                'directory': '/',
                'schedule': {'interval': 'weekly'},
                'labels': ['dependencies', 'python', 'automated'],
                'reviewers': ['arturdr']
            })
        elif language == 'javascript' or language == 'typescript':
            config['updates'].append({
                'package-ecosystem': 'npm',
                'directory': '/',
                'schedule': {'interval': 'weekly'},
                'labels': ['dependencies', 'npm', 'automated'],
                'reviewers': ['arturdr']
            })
        elif language == 'java':
            config['updates'].append({
                'package-ecosystem': 'maven',
                'directory': '/',
                'schedule': {'interval': 'weekly'},
                'labels': ['dependencies', 'java', 'automated'],
                'reviewers': ['arturdr']
            })
        elif language == 'go':
            config['updates'].append({
                'package-ecosystem': 'gomod',
                'directory': '/',
                'schedule': {'interval': 'weekly'},
                'labels': ['dependencies', 'golang', 'automated'],
                'reviewers': ['arturdr']
            })
        
        # Sempre adicionar GitHub Actions
        config['updates'].append({
            'package-ecosystem': 'github-actions',
            'directory': '/',
            'schedule': {'interval': 'weekly'},
            'labels': ['dependencies', 'github-actions', 'automated'],
            'reviewers': ['arturdr']
        })
        
        yaml_content = yaml.dump(config, default_flow_style=False)
        return base64.b64encode(yaml_content.encode()).decode()
    
    def enable_security_features(self, repo: Dict) -> Dict[str, bool]:
        """Ativar recursos de segurança avançados."""
        repo_name = repo['name']
        logger.info(f"🛡️ Ativando recursos de segurança para {repo_name}...")
        
        results = {}
        
        # Ativar vulnerability alerts
        endpoint = f"repos/{self.org_name}/{repo_name}/vulnerability-alerts"
        alert_response = self._make_request(endpoint, method='PUT')
        results['vulnerability_alerts'] = alert_response is not None
        
        # Ativar automated security fixes (Dependabot security updates)
        endpoint = f"repos/{self.org_name}/{repo_name}/automated-security-fixes"
        security_response = self._make_request(endpoint, method='PUT')
        results['automated_security_fixes'] = security_response is not None
        
        # Tentar ativar CodeQL (requer GitHub Advanced Security para repos privados)
        try:
            endpoint = f"repos/{self.org_name}/{repo_name}/code-scanning/default-setup"
            codeql_data = {"state": "configured"}
            codeql_response = self._make_request(endpoint, method='PATCH', data=codeql_data)
            results['codeql'] = codeql_response is not None
        except Exception as e:
            logger.warning(f"  ⚠️ Não foi possível ativar CodeQL: {e}")
            results['codeql'] = False
        
        logger.info(f"  ✅ Recursos de segurança configurados: {sum(results.values())}/{len(results)}")
        return results
    
    def apply_modern_branch_protection(self, repo: Dict) -> bool:
        """Aplicar proteção de branch moderna."""
        repo_name = repo['name']
        logger.info(f"🛡️ Aplicando proteção de branch moderna para {repo_name}...")
        
        # Configuração moderna de proteção
        protection_data = {
            "required_status_checks": {
                "strict": True,
                "contexts": ["ci-build-test", "security-audit"]
            },
            "enforce_admins": False,
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": True,
                "require_last_push_approval": False
            },
            "restrictions": None,  # Sem restrições de push
            "allow_force_pushes": False,
            "allow_deletions": False,
            "block_creations": False,
            "required_conversation_resolution": True
        }
        
        endpoint = f"repos/{self.org_name}/{repo_name}/branches/main/protection"
        response = self._make_request(endpoint, method='PUT', data=protection_data)
        
        if response:
            logger.info(f"  ✅ Proteção de branch aplicada em {repo_name}")
            return True
        else:
            logger.error(f"  ❌ Falha ao aplicar proteção de branch em {repo_name}")
            return False
    
    def create_modern_workflows(self, repo: Dict) -> int:
        """Criar workflows modernos baseados na linguagem do repositório."""
        repo_name = repo['name']
        language = repo.get('language', '').lower()
        
        logger.info(f"⚙️ Criando workflows modernos para {repo_name} ({language})...")
        
        workflows_created = 0
        
        # Template de CI/CD baseado na linguagem
        if language == 'python':
            workflow_content = self._get_python_modern_workflow()
            if self._create_workflow_file(repo_name, 'ci-python-modern.yml', workflow_content):
                workflows_created += 1
        elif language in ['javascript', 'typescript']:
            workflow_content = self._get_nodejs_modern_workflow()
            if self._create_workflow_file(repo_name, 'ci-nodejs-modern.yml', workflow_content):
                workflows_created += 1
        
        # Workflow de segurança universal
        security_workflow = self._get_security_workflow()
        if self._create_workflow_file(repo_name, 'security-audit.yml', security_workflow):
            workflows_created += 1
        
        logger.info(f"  ✅ {workflows_created} workflows modernos criados em {repo_name}")
        return workflows_created
    
    def _create_workflow_file(self, repo_name: str, filename: str, content: str) -> bool:
        """Criar arquivo de workflow no repositório."""
        import base64
        
        # Verificar se workflow já existe
        endpoint = f"repos/{self.org_name}/{repo_name}/contents/.github/workflows/{filename}"
        existing = self._make_request(endpoint)
        
        if existing:
            logger.info(f"    ℹ️ Workflow {filename} já existe em {repo_name}")
            return False
        
        # Criar workflow
        create_data = {
            "message": f"feat: add modern {filename} workflow",
            "content": base64.b64encode(content.encode()).decode(),
            "branch": "main"
        }
        
        response = self._make_request(endpoint, method='PUT', data=create_data)
        
        if response:
            logger.info(f"    ✅ Workflow {filename} criado em {repo_name}")
            return True
        else:
            logger.error(f"    ❌ Falha ao criar workflow {filename} em {repo_name}")
            return False
    
    def _get_python_modern_workflow(self) -> str:
        """Obter template de workflow Python modernizado."""
        return """
name: "🐍 Modern Python CI/CD"

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install black flake8 pytest pytest-cov
    - name: Code formatting
      run: black --check .
    - name: Lint check
      run: flake8 .
    - name: Run tests
      run: pytest --cov=. --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run CodeQL Analysis
      uses: github/codeql-action/analyze@v2
      with:
        languages: python
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/python@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
"""

    def _get_nodejs_modern_workflow(self) -> str:
        """Obter template de workflow Node.js modernizado."""
        return """
name: "⚡ Modern Node.js CI/CD"

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    - name: Install dependencies
      run: npm ci
    - name: Lint check
      run: npm run lint
    - name: Run tests
      run: npm test -- --coverage
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run CodeQL Analysis
      uses: github/codeql-action/analyze@v2
      with:
        languages: javascript
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
"""

    def _get_security_workflow(self) -> str:
        """Obter template de workflow de segurança universal."""
        return """
name: "🛡️ Security Audit"

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'

jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
    - uses: actions/checkout@v4
    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
    - name: Autobuild
      uses: github/codeql-action/autobuild@v2
    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
"""

    def run_modernization(self) -> Dict[str, Any]:
        """Executar modernização completa da organização."""
        logger.info("🚀 Iniciando modernização organizacional completa...")
        
        start_time = datetime.now()
        
        # Obter repositórios
        repos = self.get_organization_repos()
        
        if not repos:
            logger.error("❌ Nenhum repositório encontrado")
            return {"error": "No repositories found"}
        
        results = {
            "total_repos": len(repos),
            "processed_repos": 0,
            "dependabot_enabled": 0,
            "security_features_enabled": 0,
            "branch_protection_applied": 0,
            "modern_workflows_created": 0,
            "errors": [],
            "processing_time": None
        }
        
        # Processar cada repositório
        for i, repo in enumerate(repos, 1):
            repo_name = repo['name']
            logger.info(f"📦 Processando repositório {i}/{len(repos)}: {repo_name}")
            
            try:
                # Verificar status atual das ferramentas modernas
                current_status = self.check_modern_tools_status(repo)
                logger.info(f"  📊 Status atual: {current_status}")
                
                # Ativar Dependabot se não estiver ativo
                if not current_status.get('dependabot', False):
                    if self.enable_dependabot(repo):
                        results['dependabot_enabled'] += 1
                
                # Ativar recursos de segurança
                security_results = self.enable_security_features(repo)
                if any(security_results.values()):
                    results['security_features_enabled'] += 1
                
                # Aplicar proteção de branch moderna
                if not current_status.get('branch_protection', False):
                    if self.apply_modern_branch_protection(repo):
                        results['branch_protection_applied'] += 1
                
                # Criar workflows modernos se necessário
                if not current_status.get('modern_ci', False):
                    workflows_created = self.create_modern_workflows(repo)
                    if workflows_created > 0:
                        results['modern_workflows_created'] += workflows_created
                
                results['processed_repos'] += 1
                logger.info(f"  ✅ {repo_name} processado com sucesso")
                
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
        logger.info("🎉 MODERNIZAÇÃO ORGANIZACIONAL CONCLUÍDA!")
        logger.info("="*60)
        logger.info(f"📊 Repositórios processados: {results['processed_repos']}/{results['total_repos']}")
        logger.info(f"🤖 Dependabot ativado: {results['dependabot_enabled']} repos")
        logger.info(f"🛡️ Recursos de segurança: {results['security_features_enabled']} repos")
        logger.info(f"🔒 Proteção de branches: {results['branch_protection_applied']} repos")
        logger.info(f"⚙️ Workflows modernos: {results['modern_workflows_created']} criados")
        logger.info(f"⏱️ Tempo total: {results['processing_time']}")
        
        if results['errors']:
            logger.warning(f"⚠️ Erros encontrados: {len(results['errors'])}")
            for error in results['errors']:
                logger.warning(f"  • {error}")
        
        # Salvar relatório
        report_file = self.root_dir / f"modernization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📄 Relatório salvo em: {report_file}")
        
        return results


def main():
    """Função principal."""
    try:
        automation = ModernizedOrganizationAutomation()
        results = automation.run_modernization()
        
        # Código de saída baseado no sucesso
        if results.get('errors'):
            sys.exit(1)  # Houve erros
        else:
            sys.exit(0)  # Sucesso completo
            
    except Exception as e:
        logger.error(f"❌ Erro fatal na modernização: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()