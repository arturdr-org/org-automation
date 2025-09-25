#!/usr/bin/env python3
"""
Script de Teste e Validação da Configuração
Verifica se o sistema está corretamente configurado antes de executar em produção.
"""

import os
import sys
import requests
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# Cores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message: str, status: str) -> None:
    """Imprime mensagem com status colorido."""
    if status == "ok":
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    elif status == "error":
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    else:
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_header(title: str) -> None:
    """Imprime cabeçalho de seção."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}{Colors.END}\n")

class ConfigurationValidator:
    """Classe para validar configuração do sistema."""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / "config"
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.total_checks = 0
    
    def check_python_version(self) -> bool:
        """Verifica versão do Python."""
        self.total_checks += 1
        version = sys.version_info
        
        if version.major >= 3 and version.minor >= 8:
            print_status(f"Python {version.major}.{version.minor}.{version.micro}", "ok")
            self.checks_passed += 1
            return True
        else:
            print_status(f"Python {version.major}.{version.minor} - Versão 3.8+ necessária", "error")
            self.errors.append("Versão do Python incompatível")
            return False
    
    def check_dependencies(self) -> bool:
        """Verifica se todas as dependências estão instaladas."""
        self.total_checks += 1
        required_modules = ["requests", "yaml"]
        missing = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        if not missing:
            print_status("Todas as dependências instaladas", "ok")
            self.checks_passed += 1
            return True
        else:
            print_status(f"Dependências faltando: {', '.join(missing)}", "error")
            self.errors.append(f"Instale: pip install {' '.join(missing)}")
            return False
    
    def check_environment_variables(self) -> bool:
        """Verifica variáveis de ambiente."""
        self.total_checks += 1
        token = os.getenv("ORG_AUTOMATION_PAT") or os.getenv("GITHUB_TOKEN")
        org_name = os.getenv("ORG_NAME", "arturdr-org")
        
        if token:
            print_status(f"Token encontrado (✱✱✱✱{token[-4:]})", "ok")
            if org_name == "arturdr-org":
                print_status(f"Organização: {org_name}", "ok")
                self.checks_passed += 1
                return True
            else:
                print_status(f"Organização: {org_name} - Verificar se está correto", "warning")
                self.warnings.append(f"Organização configurada: {org_name}")
                self.checks_passed += 1
                return True
        else:
            print_status("Token não encontrado - Configure ORG_AUTOMATION_PAT", "error")
            self.errors.append("Configure ORG_AUTOMATION_PAT ou GITHUB_TOKEN")
            return False
    
    def check_github_connectivity(self) -> bool:
        """Verifica conectividade com GitHub API."""
        self.total_checks += 1
        token = os.getenv("ORG_AUTOMATION_PAT") or os.getenv("GITHUB_TOKEN")
        
        if not token:
            print_status("Não é possível testar conectividade sem token", "error")
            return False
        
        try:
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                print_status(f"Conectado como: {user_data.get('login', 'Unknown')}", "ok")
                self.checks_passed += 1
                return True
            else:
                print_status(f"Erro de autenticação: HTTP {response.status_code}", "error")
                self.errors.append("Token inválido ou sem permissões")
                return False
                
        except Exception as e:
            print_status(f"Erro de conectividade: {str(e)}", "error")
            self.errors.append("Não foi possível conectar ao GitHub")
            return False
    
    def check_organization_access(self) -> bool:
        """Verifica acesso à organização."""
        self.total_checks += 1
        token = os.getenv("ORG_AUTOMATION_PAT") or os.getenv("GITHUB_TOKEN")
        org_name = os.getenv("ORG_NAME", "arturdr-org")
        
        if not token:
            print_status("Não é possível testar sem token", "error")
            return False
        
        try:
            headers = {"Authorization": f"token {token}"}
            response = requests.get(f"https://api.github.com/orgs/{org_name}/repos", 
                                  headers=headers, timeout=10, params={"per_page": 1})
            
            if response.status_code == 200:
                repos_data = response.json()
                print_status(f"Acesso à organização {org_name} confirmado", "ok")
                self.checks_passed += 1
                return True
            elif response.status_code == 404:
                print_status(f"Organização {org_name} não encontrada", "error")
                self.errors.append(f"Organização {org_name} não existe ou sem acesso")
                return False
            else:
                print_status(f"Erro de acesso: HTTP {response.status_code}", "error")
                self.errors.append("Token sem permissões para a organização")
                return False
                
        except Exception as e:
            print_status(f"Erro ao acessar organização: {str(e)}", "error")
            return False
    
    def check_config_files(self) -> bool:
        """Verifica arquivos de configuração."""
        self.total_checks += 1
        required_files = [
            "labels.yml",
            "branch_protection.yml",
            "CODEOWNERS",
        ]
        
        missing_files = []
        invalid_files = []
        
        # Verificar arquivos principais
        for file_name in required_files:
            file_path = self.config_dir / file_name
            if not file_path.exists():
                missing_files.append(file_name)
            elif file_name.endswith('.yml'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    invalid_files.append(f"{file_name}: {str(e)}")
        
        # Verificar templates
        templates_dir = self.config_dir / "templates"
        if templates_dir.exists():
            template_files = ["bug_report.md", "feature_request.md", "pull_request_template.md"]
            for template in template_files:
                if not (templates_dir / template).exists():
                    missing_files.append(f"templates/{template}")
        else:
            missing_files.append("templates/ (diretório)")
        
        if not missing_files and not invalid_files:
            print_status("Todos os arquivos de configuração presentes e válidos", "ok")
            self.checks_passed += 1
            return True
        else:
            if missing_files:
                print_status(f"Arquivos faltando: {', '.join(missing_files)}", "error")
                self.errors.extend([f"Arquivo faltando: {f}" for f in missing_files])
            if invalid_files:
                print_status(f"Arquivos inválidos: {', '.join(invalid_files)}", "error")
                self.errors.extend([f"YAML inválido: {f}" for f in invalid_files])
            return False
    
    def check_workflows(self) -> bool:
        """Verifica workflows do GitHub Actions."""
        self.total_checks += 1
        workflows_dir = Path(__file__).parent / ".github" / "workflows"
        
        if not workflows_dir.exists():
            print_status("Diretório .github/workflows não encontrado", "error")
            self.errors.append("Diretório de workflows não existe")
            return False
        
        required_workflows = [
            "enhanced-automation.yml",
            "health-monitoring.yml"
        ]
        
        missing_workflows = []
        for workflow in required_workflows:
            if not (workflows_dir / workflow).exists():
                missing_workflows.append(workflow)
        
        if not missing_workflows:
            print_status("Todos os workflows necessários presentes", "ok")
            self.checks_passed += 1
            return True
        else:
            print_status(f"Workflows faltando: {', '.join(missing_workflows)}", "error")
            self.errors.extend([f"Workflow faltando: {w}" for w in missing_workflows])
            return False
    
    def check_scripts(self) -> bool:
        """Verifica scripts principais."""
        self.total_checks += 1
        script_dir = Path(__file__).parent
        required_scripts = [
            "enhanced_automation.py",
            "monitoring.py",
        ]
        
        missing_scripts = []
        for script in required_scripts:
            script_path = script_dir / script
            if not script_path.exists():
                missing_scripts.append(script)
            else:
                # Verificar se o script pode ser importado
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("test_module", script_path)
                    # Só verifica se o arquivo pode ser lido, sem executar
                except Exception as e:
                    print_status(f"Erro em {script}: {str(e)}", "warning")
                    self.warnings.append(f"Possível problema em {script}")
        
        if not missing_scripts:
            print_status("Todos os scripts principais presentes", "ok")
            self.checks_passed += 1
            return True
        else:
            print_status(f"Scripts faltando: {', '.join(missing_scripts)}", "error")
            self.errors.extend([f"Script faltando: {s}" for s in missing_scripts])
            return False
    
    def run_dry_run_test(self) -> bool:
        """Executa teste em modo dry-run."""
        self.total_checks += 1
        print_status("Executando teste dry-run...", "info")
        
        try:
            # Importar e executar o script principal em modo dry-run
            os.environ["DRY_RUN"] = "true"
            
            # Verificar se o script pode ser importado
            sys.path.insert(0, str(Path(__file__).parent))
            
            try:
                import enhanced_automation
                print_status("Script enhanced_automation.py importado com sucesso", "ok")
                
                # Tentar criar a instância (mas não executar)
                automation = enhanced_automation.OrganizationAutomation()
                print_status("Configurações carregadas com sucesso", "ok")
                
                self.checks_passed += 1
                return True
                
            except Exception as e:
                print_status(f"Erro ao importar/configurar: {str(e)}", "error")
                self.errors.append(f"Erro no script principal: {str(e)}")
                return False
                
        except Exception as e:
            print_status(f"Erro no teste dry-run: {str(e)}", "error")
            self.errors.append(f"Falha no teste: {str(e)}")
            return False
        finally:
            os.environ.pop("DRY_RUN", None)
    
    def print_summary(self) -> bool:
        """Imprime resumo final."""
        print_header("RESUMO DA VALIDAÇÃO")
        
        print(f"✅ Verificações passaram: {self.checks_passed}/{self.total_checks}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}⚠️  AVISOS:{Colors.END}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.errors:
            print(f"\n{Colors.RED}❌ ERROS:{Colors.END}")
            for error in self.errors:
                print(f"   • {error}")
        
        success_rate = (self.checks_passed / self.total_checks) * 100 if self.total_checks > 0 else 0
        
        print(f"\n{Colors.BOLD}STATUS GERAL:{Colors.END}")
        if success_rate == 100 and not self.errors:
            print_status(f"CONFIGURAÇÃO VÁLIDA ({success_rate:.1f}%)", "ok")
            print(f"\n{Colors.GREEN}🎉 Sistema pronto para execução!{Colors.END}")
            return True
        elif success_rate >= 80 and not self.errors:
            print_status(f"CONFIGURAÇÃO ACEITÁVEL ({success_rate:.1f}%)", "warning")
            print(f"\n{Colors.YELLOW}⚠️  Sistema pode funcionar, mas há avisos.{Colors.END}")
            return True
        else:
            print_status(f"CONFIGURAÇÃO COM PROBLEMAS ({success_rate:.1f}%)", "error")
            print(f"\n{Colors.RED}❌ Corrija os erros antes de executar em produção.{Colors.END}")
            return False
    
    def run_all_checks(self) -> bool:
        """Executa todas as verificações."""
        print_header("VALIDAÇÃO DO SISTEMA DE AUTOMAÇÃO")
        print(f"Organização: {Colors.BOLD}arturdr-org{Colors.END}\n")
        
        checks = [
            ("Versão do Python", self.check_python_version),
            ("Dependências", self.check_dependencies),
            ("Variáveis de Ambiente", self.check_environment_variables),
            ("Conectividade GitHub", self.check_github_connectivity),
            ("Acesso à Organização", self.check_organization_access),
            ("Arquivos de Configuração", self.check_config_files),
            ("Workflows", self.check_workflows),
            ("Scripts", self.check_scripts),
            ("Teste Dry-Run", self.run_dry_run_test),
        ]
        
        for name, check_func in checks:
            print_header(name)
            check_func()
        
        return self.print_summary()


def main():
    """Função principal."""
    validator = ConfigurationValidator()
    success = validator.run_all_checks()
    
    # Exit code baseado no resultado
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()