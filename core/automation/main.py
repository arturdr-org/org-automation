#!/usr/bin/env python3
"""
Enhanced Org Automation Script para arturdr-org
Sistema completo de padronização e automação usando configurações centralizadas.
"""

import os
import sys
import time
import base64
import yaml
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('automation.log')
    ]
)
logger = logging.getLogger(__name__)

# Configurações
ORG_NAME = os.getenv("ORG_NAME", "arturdr-org")
PROJECT_NUMBER = int(os.getenv("PROJECT_NUMBER", "1"))
TOKEN = os.getenv("ORG_AUTOMATION_PAT") or os.getenv("GITHUB_TOKEN")
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

if not TOKEN:
    logger.error("Token não encontrado. Defina ORG_AUTOMATION_PAT ou GITHUB_TOKEN")
    sys.exit(1)

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

GRAPHQL_HEADERS = {
    "Authorization": f"bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# Caminhos para arquivos de configuração
CONFIG_DIR = Path(__file__).parent.parent.parent / "common/config"
LABELS_CONFIG = CONFIG_DIR / "labels.yml"
BRANCH_PROTECTION_CONFIG = CONFIG_DIR / "branch_protection.yml"
TEMPLATES_DIR = CONFIG_DIR / "templates"


class OrganizationAutomation:
    """Classe principal para automação da organização."""
    
    def __init__(self):
        self.org_name = ORG_NAME
        self.project_id = None
        self.stats = {
            "repos_processed": 0,
            "labels_created": 0,
            "labels_updated": 0,
            "templates_created": 0,
            "protections_applied": 0,
            "issues_created": 0,
            "errors": []
        }
        
        # Carregar configurações
        self.load_configurations()
    
    def load_configurations(self) -> None:
        """Carrega todas as configurações dos arquivos YAML."""
        try:
            # Labels
            if LABELS_CONFIG.exists():
                with open(LABELS_CONFIG, 'r', encoding='utf-8') as f:
                    self.labels_config = yaml.safe_load(f)
                logger.info(f"Configuração de labels carregada: {len(self.get_all_labels())} labels")
            else:
                logger.warning("Arquivo de configuração de labels não encontrado")
                self.labels_config = {"default_labels": [], "org_labels": []}
            
            # Proteções de branch
            if BRANCH_PROTECTION_CONFIG.exists():
                with open(BRANCH_PROTECTION_CONFIG, 'r', encoding='utf-8') as f:
                    self.branch_protection_config = yaml.safe_load(f)
                logger.info("Configuração de proteção de branches carregada")
            else:
                logger.warning("Arquivo de configuração de proteção de branches não encontrado")
                self.branch_protection_config = {}
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            sys.exit(1)
    
    def get_all_labels(self) -> List[Dict]:
        """Retorna todas as labels (default + org)."""
        all_labels = []
        all_labels.extend(self.labels_config.get("default_labels", []))
        all_labels.extend(self.labels_config.get("org_labels", []))
        return all_labels
    
    def list_repos(self) -> List[Dict]:
        """Lista todos os repositórios da organização."""
        repos = []
        page = 1
        
        try:
            while True:
                url = f"https://api.github.com/orgs/{self.org_name}/repos"
                r = requests.get(
                    url,
                    headers=HEADERS,
                    params={"per_page": 100, "page": page, "type": "all"},
                    timeout=30,
                )
                
                if r.status_code in (401, 403):
                    logger.warning("Acesso negado ao endpoint da org, tentando fallback...")
                    return self._fallback_list_repos()
                
                r.raise_for_status()
                data = r.json()
                if not data:
                    break
                    
                repos.extend(data)
                page += 1
                time.sleep(0.1)
                
            logger.info(f"Encontrados {len(repos)} repositórios na organização")
            return repos
            
        except Exception as e:
            logger.error(f"Erro ao listar repositórios: {e}")
            return []
    
    def _fallback_list_repos(self) -> List[Dict]:
        """Fallback para listar repos via instalação do App."""
        repos = []
        page = 1
        
        try:
            while True:
                r = requests.get(
                    "https://api.github.com/installation/repositories",
                    headers=HEADERS,
                    params={"per_page": 100, "page": page},
                    timeout=30,
                )
                r.raise_for_status()
                payload = r.json()
                data = payload.get("repositories", [])
                if not data:
                    break
                
                # Filtrar apenas repos da nossa organização
                for repo in data:
                    if repo.get("owner", {}).get("login") == self.org_name:
                        repos.append(repo)
                
                page += 1
                time.sleep(0.1)
                
            return repos
            
        except Exception as e:
            logger.error(f"Erro no fallback de listagem de repos: {e}")
            return []
    
    def ensure_label(self, repo_name: str, label: Dict) -> bool:
        """Cria ou atualiza uma label em um repositório."""
        if DRY_RUN:
            logger.info(f"[DRY-RUN] Criaria/atualizaria label '{label['name']}' em {repo_name}")
            return True
        
        url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/labels"
        
        # Tentar criar a label
        resp = requests.post(
            url, 
            headers=HEADERS, 
            json=label,
            timeout=30
        )
        
        if resp.status_code in (200, 201):
            logger.info(f"Label '{label['name']}' criada em {repo_name}")
            self.stats["labels_created"] += 1
            return True
        elif resp.status_code == 422:
            # Label já existe, tentar atualizar
            patch_url = f"{url}/{label['name']}"
            patch_resp = requests.patch(
                patch_url,
                headers=HEADERS,
                json={
                    "new_name": label["name"],
                    "color": label["color"],
                    "description": label.get("description", "")
                },
                timeout=30,
            )
            if patch_resp.ok:
                logger.info(f"Label '{label['name']}' atualizada em {repo_name}")
                self.stats["labels_updated"] += 1
                return True
            else:
                logger.warning(f"Falha ao atualizar label '{label['name']}' em {repo_name}: {patch_resp.status_code}")
                return False
        else:
            logger.warning(f"Falha ao criar label '{label['name']}' em {repo_name}: {resp.status_code}")
            return False
    
    def ensure_file(self, repo_name: str, file_path: str, content: str, commit_message: str) -> bool:
        """Cria um arquivo se ele não existir."""
        if DRY_RUN:
            logger.info(f"[DRY-RUN] Criaria arquivo {file_path} em {repo_name}")
            return True
        
        url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/contents/{file_path}"
        
        # Verificar se arquivo já existe
        check_resp = requests.get(url, headers=HEADERS, timeout=30)
        if check_resp.status_code == 200:
            logger.info(f"Arquivo {file_path} já existe em {repo_name} - preservando")
            return True
        elif check_resp.status_code != 404:
            logger.warning(f"Erro ao verificar arquivo {file_path} em {repo_name}: {check_resp.status_code}")
            return False
        
        # Criar arquivo
        payload = {
            "message": commit_message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        }
        
        create_resp = requests.put(url, headers=HEADERS, json=payload, timeout=30)
        if create_resp.status_code in (201, 200):
            logger.info(f"Arquivo {file_path} criado em {repo_name}")
            self.stats["templates_created"] += 1
            return True
        else:
            logger.warning(f"Falha ao criar arquivo {file_path} em {repo_name}: {create_resp.status_code}")
            self.stats["errors"].append(f"Falha ao criar {file_path} em {repo_name}")
            return False
    
    def setup_templates(self, repo_name: str) -> None:
        """Configura todos os templates padrão."""
        templates = [
            {
                "path": ".github/ISSUE_TEMPLATE/bug_report.md",
                "source": TEMPLATES_DIR / "bug_report.md",
                "message": "chore: add bug report template"
            },
            {
                "path": ".github/ISSUE_TEMPLATE/feature_request.md",
                "source": TEMPLATES_DIR / "feature_request.md",
                "message": "chore: add feature request template"
            },
            {
                "path": ".github/PULL_REQUEST_TEMPLATE.md",
                "source": TEMPLATES_DIR / "pull_request_template.md",
                "message": "chore: add PR template"
            },
            {
                "path": ".github/CODEOWNERS",
                "source": CONFIG_DIR / "CODEOWNERS",
                "message": "chore: add CODEOWNERS file"
            }
        ]
        
        for template in templates:
            if template["source"].exists():
                with open(template["source"], 'r', encoding='utf-8') as f:
                    content = f.read()
                self.ensure_file(repo_name, template["path"], content, template["message"])
            else:
                logger.warning(f"Template {template['source']} não encontrado")
    
    def setup_workflow_templates(self, repo_name: str, repo_info: Dict) -> None:
        """Configura templates de workflows CI/CD baseado na linguagem do repositório."""
        workflow_templates_dir = Path(__file__).parent / "workflow-templates"
        
        # Detectar linguagem principal do repositório
        primary_language = repo_info.get("language", "").lower() if repo_info.get("language") else ""
        
        templates_to_apply = []
        
        # Mapear linguagens para templates apropriados
        if primary_language in ["python"]:
            templates_to_apply.extend([
                {
                    "path": ".github/workflows/python-ci.yml",
                    "source": workflow_templates_dir / "python-ci.yml",
                    "message": "chore: add Python CI/CD pipeline"
                }
            ])
        elif primary_language in ["javascript", "typescript"]:
            templates_to_apply.extend([
                {
                    "path": ".github/workflows/nodejs-ci.yml",
                    "source": workflow_templates_dir / "nodejs-ci.yml",
                    "message": "chore: add Node.js CI/CD pipeline"
                }
            ])
        
        # Sempre aplicar template de release automation se não existir
        templates_to_apply.append({
            "path": ".github/workflows/release-automation.yml",
            "source": workflow_templates_dir / "release-automation.yml",
            "message": "chore: add release automation workflow"
        })
        
        # Template básico de CI se nenhuma linguagem específica foi detectada
        if not primary_language or primary_language not in ["python", "javascript", "typescript"]:
            basic_ci_content = """
name: 🔍 Basic CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  basic-checks:
    name: 🔍 Basic Quality Checks
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Checkout Code
        uses: actions/checkout@v4

      - name: 📋 YAML Lint
        uses: ibiqlik/action-yamllint@v1
        with:
          files: '**/*.yml **/*.yaml'
          
      - name: 🔍 Markdown Link Check
        uses: gaurav-nelson/github-action-markdown-link-check@v1
        with:
          use-quiet-mode: 'yes'
          use-verbose-mode: 'yes'
          config-file: '.mlc_config.json'
          
      - name: 🎨 Prettier Check
        run: |
          if [ -f package.json ]; then
            npm install prettier
            npx prettier --check "**/*.{json,md,yml,yaml}" || echo "Prettier check completed"
          else
            echo "No package.json found, skipping Prettier check"
          fi
"""
            templates_to_apply.append({
                "path": ".github/workflows/basic-ci.yml",
                "content": basic_ci_content,
                "message": "chore: add basic CI workflow"
            })
        
        # Aplicar templates
        for template in templates_to_apply:
            if "source" in template and template["source"].exists():
                with open(template["source"], 'r', encoding='utf-8') as f:
                    content = f.read()
                self.ensure_file(repo_name, template["path"], content, template["message"])
            elif "content" in template:
                self.ensure_file(repo_name, template["path"], template["content"], template["message"])
            else:
                logger.warning(f"Template source {template.get('source', 'unknown')} não encontrado")
    
    def apply_branch_protection(self, repo_name: str) -> None:
        """Aplica proteções de branch conforme configuração."""
        if DRY_RUN:
            logger.info(f"[DRY-RUN] Aplicaria proteções de branch em {repo_name}")
            return
        
        # Listar branches existentes
        branches_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/branches"
        branches_resp = requests.get(branches_url, headers=HEADERS, timeout=30)
        
        if not branches_resp.ok:
            logger.warning(f"Não foi possível listar branches de {repo_name}")
            return
        
        branches = branches_resp.json()
        branch_names = [b["name"] for b in branches]
        
        # Aplicar proteções configuradas
        branch_config = self.branch_protection_config.get("branch_protection", {})
        auto_patterns = self.branch_protection_config.get("auto_protect_patterns", [])
        
        for branch_name in branch_names:
            # Verificar se deve aplicar proteção
            should_protect = False
            config_key = None
            
            # Verificar padrões automáticos
            for pattern in auto_patterns:
                if pattern.replace("*", "") in branch_name or branch_name == pattern:
                    should_protect = True
                    break
            
            # Determinar qual configuração usar
            if branch_name in branch_config:
                config_key = branch_name
            elif branch_name == "master" and "main" in branch_config:
                config_key = "main"
            elif branch_name in ["dev", "develop"] and "develop" in branch_config:
                config_key = "develop"
            
            if should_protect and config_key:
                self._apply_branch_protection_rules(repo_name, branch_name, branch_config[config_key])
    
    def _apply_branch_protection_rules(self, repo_name: str, branch_name: str, protection_config: Dict) -> None:
        """Aplica regras específicas de proteção a um branch."""
        url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/branches/{branch_name}/protection"
        
        payload = {
            "required_status_checks": protection_config.get("required_status_checks"),
            "enforce_admins": protection_config.get("enforce_admins", False),
            "required_pull_request_reviews": protection_config.get("required_pull_request_reviews"),
            "restrictions": protection_config.get("restrictions"),
            "allow_force_pushes": protection_config.get("allow_force_pushes", False),
            "allow_deletions": protection_config.get("allow_deletions", False),
        }
        
        # Remover chaves None
        payload = {k: v for k, v in payload.items() if v is not None}
        
        resp = requests.put(url, headers=HEADERS, json=payload, timeout=30)
        
        if resp.ok:
            logger.info(f"Proteção aplicada ao branch '{branch_name}' em {repo_name}")
            self.stats["protections_applied"] += 1
        else:
            logger.warning(f"Falha ao proteger branch '{branch_name}' em {repo_name}: {resp.status_code}")
            self.stats["errors"].append(f"Falha proteção branch {branch_name} em {repo_name}")
    
    def create_automation_issue(self, repo_name: str) -> None:
        """Cria issue de checklist de automação se não existir."""
        issue_title = "🔧 Checklist de Automação da Organização"
        issue_body = """
Este issue tracked o status da padronização deste repositório conforme as diretrizes da organização `arturdr-org`.

## ✅ Checklist

### 🏷️ Labels
- [ ] Labels padrão aplicadas
- [ ] Labels personalizadas da organização configuradas

### 📋 Templates
- [ ] Template de bug report configurado
- [ ] Template de feature request configurado  
- [ ] Template de Pull Request configurado
- [ ] Arquivo CODEOWNERS configurado

### 🔒 Proteções
- [ ] Proteções de branch aplicadas
- [ ] Regras de revisão configuradas

### 🔄 Workflows
- [ ] Workflow básico de CI configurado
- [ ] Validações automatizadas ativas

### 📊 Projeto
- [ ] Repositório vinculado ao projeto da organização

---
*Este issue foi criado automaticamente pelo sistema de automação da organização.*
        """
        
        if DRY_RUN:
            logger.info(f"[DRY-RUN] Criaria issue de automação em {repo_name}")
            return
        
        # Verificar se já existe
        issues_url = f"https://api.github.com/repos/{self.org_name}/{repo_name}/issues"
        search_resp = requests.get(
            issues_url,
            headers=HEADERS,
            params={"state": "all", "creator": "app/org-automation"},
            timeout=30
        )
        
        if search_resp.ok:
            existing_issues = search_resp.json()
            for issue in existing_issues:
                if issue_title in issue.get("title", ""):
                    logger.info(f"Issue de automação já existe em {repo_name}")
                    return
        
        # Criar issue
        create_resp = requests.post(
            issues_url,
            headers=HEADERS,
            json={
                "title": issue_title,
                "body": issue_body.strip(),
                "labels": ["automation", "priority:medium"]
            },
            timeout=30
        )
        
        if create_resp.status_code in (200, 201):
            logger.info(f"Issue de automação criada em {repo_name}")
            self.stats["issues_created"] += 1
        else:
            logger.warning(f"Falha ao criar issue em {repo_name}: {create_resp.status_code}")
    
    def process_repository(self, repo: Dict) -> None:
        """Processa um repositório aplicando todas as padronizações."""
        repo_name = repo["name"]
        logger.info(f"\n🔄 Processando repositório: {repo_name}")
        
        try:
            # 1. Aplicar labels
            labels = self.get_all_labels()
            for label in labels:
                self.ensure_label(repo_name, label)
            
            # 2. Configurar templates
            self.setup_templates(repo_name)
            
            # 3. Configurar workflows CI/CD
            self.setup_workflow_templates(repo_name, repo)
            
            # 4. Aplicar proteções de branch
            self.apply_branch_protection(repo_name)
            
            # 5. Criar issue de automação
            self.create_automation_issue(repo_name)
            
            self.stats["repos_processed"] += 1
            logger.info(f"✅ Repositório {repo_name} processado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar {repo_name}: {e}")
            self.stats["errors"].append(f"Erro em {repo_name}: {str(e)}")
    
    def generate_report(self) -> None:
        """Gera relatório final da execução."""
        report = f"""
{'='*60}
📊 RELATÓRIO DE AUTOMAÇÃO DA ORGANIZAÇÃO
{'='*60}

🏢 Organização: {self.org_name}
⏰ Executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🧪 Modo: {'DRY-RUN' if DRY_RUN else 'PRODUÇÃO'}

📈 ESTATÍSTICAS:
  📁 Repositórios processados: {self.stats['repos_processed']}
  🏷️ Labels criadas: {self.stats['labels_created']}
  🏷️ Labels atualizadas: {self.stats['labels_updated']}
  📄 Templates criados: {self.stats['templates_created']}
  🔒 Proteções aplicadas: {self.stats['protections_applied']}
  📋 Issues criadas: {self.stats['issues_created']}
  ❌ Erros: {len(self.stats['errors'])}

"""
        if self.stats["errors"]:
            report += "❌ ERROS ENCONTRADOS:\n"
            for error in self.stats["errors"]:
                report += f"  - {error}\n"
        
        report += f"\n{'='*60}\n"
        
        print(report)
        logger.info("Relatório de automação gerado")
        
        # Salvar relatório em arquivo
        report_file = f"automation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Relatório salvo em {report_file}")
    
    def run(self) -> None:
        """Executa o processo completo de automação."""
        logger.info(f"🚀 Iniciando automação da organização {self.org_name}")
        
        if DRY_RUN:
            logger.info("🧪 Executando em modo DRY-RUN (sem alterações)")
        
        # Listar repositórios
        repos = self.list_repos()
        if not repos:
            logger.error("Nenhum repositório encontrado")
            return
        
        # Processar cada repositório
        for repo in repos:
            if not repo.get("archived", False):  # Pular repos arquivados
                self.process_repository(repo)
                time.sleep(0.5)  # Rate limiting
            else:
                logger.info(f"⏭️ Pulando repositório arquivado: {repo['name']}")
        
        # Gerar relatório final
        self.generate_report()
        
        logger.info("🎉 Automação concluída!")


def main():
    """Função principal."""
    try:
        automation = OrganizationAutomation()
        automation.run()
    except KeyboardInterrupt:
        logger.info("❌ Automação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()