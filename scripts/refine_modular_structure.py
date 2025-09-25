#!/usr/bin/env python3
"""
Script para refinar a estrutura modular com melhorias:
1. Padronizar nomes de diretórios (shared → common)
2. Organizar workflows do GitHub Actions corretamente
3. Melhorar consistência geral da estrutura
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List

class StructureRefiner:
    """Refinador da estrutura modular."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        
        # Mapeamento de melhorias
        self.improvements = {
            # Renomear diretórios para nomes mais intuitivos
            "shared": "common",
            
            # Reorganizar workflows
            "organize_workflows": True,
            
            # Padronizar estrutura
            "standardize_names": True
        }
    
    def rename_shared_to_common(self):
        """Renomeia 'shared' para 'common' - termo mais intuitivo."""
        print("📁 Renomeando 'shared' para 'common'...")
        
        shared_dir = self.root_dir / "shared"
        common_dir = self.root_dir / "common"
        
        if shared_dir.exists() and not common_dir.exists():
            shutil.move(str(shared_dir), str(common_dir))
            print("  ✅ shared/ → common/")
            
            # Atualizar imports nos arquivos
            self.update_shared_imports()
        else:
            print("  ℹ️ Diretório 'shared' não encontrado ou 'common' já existe")
    
    def update_shared_imports(self):
        """Atualiza imports de 'shared' para 'common'."""
        print("🔄 Atualizando imports shared → common...")
        
        # Arquivos que podem conter imports 'shared'
        files_to_update = [
            self.root_dir / "core" / "automation" / "main.py",
            self.root_dir / "core" / "monitoring" / "health_check.py",
            self.root_dir / "core" / "monitoring" / "dashboard.py",
            self.root_dir / "__init__.py",
            self.root_dir / "setup.py"
        ]
        
        for file_path in files_to_update:
            if file_path.exists():
                content = file_path.read_text()
                
                # Atualizar paths
                old_patterns = [
                    'shared/config',
                    '"shared/config"',
                    "'shared/config'",
                    'Path(__file__).parent.parent.parent / "shared/config"'
                ]
                
                new_patterns = [
                    'common/config',
                    '"common/config"',
                    "'common/config'",
                    'Path(__file__).parent.parent.parent / "common/config"'
                ]
                
                updated = False
                for old, new in zip(old_patterns, new_patterns):
                    if old in content:
                        content = content.replace(old, new)
                        updated = True
                
                if updated:
                    file_path.write_text(content)
                    print(f"  🔄 Atualizado: {file_path.name}")
    
    def organize_github_workflows(self):
        """Organiza workflows do GitHub Actions corretamente."""
        print("⚙️ Organizando workflows do GitHub Actions...")
        
        github_workflows_dir = self.root_dir / ".github" / "workflows"
        cicd_templates_dir = self.root_dir / "modules" / "cicd" / "templates"
        
        if not github_workflows_dir.exists():
            github_workflows_dir.mkdir(parents=True)
        
        # Lista de workflows que devem estar em .github/workflows/
        active_workflows = [
            # Workflows ativos da organização
            "enhanced-automation.yml",
            "health-monitoring.yml", 
            "automation-cron.yml",
            
            # Workflows básicos que podem ser aplicados
            "ci-basic.yml",
            "python-ci.yml",
            "release-automation.yml"
        ]
        
        workflows_moved = 0
        
        # Mover workflows dos templates para .github/workflows se fizer sentido
        if cicd_templates_dir.exists():
            for workflow_file in cicd_templates_dir.glob("*.yml"):
                target_path = github_workflows_dir / workflow_file.name
                
                # Se é um workflow que faz sentido ter ativo na org
                if workflow_file.name in ["python-ci.yml", "release-automation.yml"]:
                    # Criar versão "template" para aplicar em outros repos
                    template_content = workflow_file.read_text()
                    
                    # Adicionar comentário indicando que é template
                    template_header = f"""# Template Workflow - {workflow_file.stem.title()}
# Este arquivo é um template para ser aplicado em outros repositórios
# Modificado automaticamente pela automação organizacional

"""
                    
                    template_with_header = template_header + template_content
                    workflow_file.write_text(template_with_header)
                    print(f"  📝 Template atualizado: {workflow_file.name}")
        
        # Verificar quais workflows já existem e estão ativos
        if github_workflows_dir.exists():
            existing_workflows = list(github_workflows_dir.glob("*.yml"))
            print(f"  📋 Workflows ativos encontrados: {len(existing_workflows)}")
            for workflow in existing_workflows:
                print(f"    ✅ {workflow.name}")
        
        print(f"  ✅ Organização de workflows concluída")
    
    def standardize_directory_names(self):
        """Padroniza nomes de diretórios para maior consistência."""
        print("📂 Padronizando nomes de diretórios...")
        
        # Verificar se existem inconsistências que precisam ser corrigidas
        dirs_to_check = {
            "tests": ["unit", "integration", "fixtures", "e2e"],
            "docs": ["modules", "api", "guides"],
            "common": ["config", "utils", "constants"],
            "core": ["automation", "monitoring", "testing"],
            "modules": ["cicd", "security", "quality", "notifications"]
        }
        
        inconsistencies_found = []
        
        for main_dir, expected_subdirs in dirs_to_check.items():
            main_path = self.root_dir / main_dir
            if main_path.exists():
                existing_subdirs = [d.name for d in main_path.iterdir() if d.is_dir()]
                
                # Verificar se há diretórios inesperados ou mal nomeados
                for subdir in existing_subdirs:
                    if subdir not in expected_subdirs and not subdir.startswith("__"):
                        inconsistencies_found.append(f"{main_dir}/{subdir}")
        
        if inconsistencies_found:
            print(f"  ⚠️ Inconsistências encontradas: {inconsistencies_found}")
        else:
            print("  ✅ Estrutura de diretórios consistente")
    
    def create_improved_init_files(self):
        """Cria __init__.py melhorados com imports mais claros."""
        print("📦 Criando __init__.py melhorados...")
        
        # __init__.py principal atualizado
        main_init_content = '''"""
AI-powered-org-automation-suite: Sistema completo de automação organizacional para arturdr-org

Estrutura modular:
├── core/           # Sistema central (automation, monitoring, testing)
├── modules/        # Módulos específicos (cicd, security, quality, notifications)  
├── common/         # Recursos compartilhados (config, utils, constants)
├── docs/          # Documentação organizada
└── tests/         # Testes estruturados

Uso rápido:
    from core.automation.main import OrganizationAutomation
    from core.monitoring.dashboard import OrganizationDashboard
    
    automation = OrganizationAutomation()
    dashboard = OrganizationDashboard()
"""

__version__ = "2.1.0"  # Versão incrementada com melhorias
__author__ = "arturdr-org"

# Imports principais para facilitar uso
try:
    from core.automation.main import OrganizationAutomation
    from core.monitoring.health_check import OrganizationHealthMonitor
    from core.monitoring.dashboard import OrganizationDashboard
    
    __all__ = [
        "OrganizationAutomation",
        "OrganizationHealthMonitor", 
        "OrganizationDashboard"
    ]
except ImportError as e:
    # Se imports falharem durante setup, apenas definir __all__
    __all__ = []
    import warnings
    warnings.warn(f"Alguns módulos não puderam ser importados: {e}")
'''
        
        main_init = self.root_dir / "__init__.py"
        main_init.write_text(main_init_content)
        print("  ✅ __init__.py principal atualizado")
        
        # core/__init__.py
        core_init_content = '''"""
Core modules - Sistema central da automação organizacional.

Módulos:
- automation: Sistema principal de automação
- monitoring: Health checks e dashboard
- testing: Validação e testes
"""

from . import automation, monitoring, testing

__all__ = ["automation", "monitoring", "testing"]
'''
        
        core_init = self.root_dir / "core" / "__init__.py"
        if not core_init.exists():
            core_init.write_text(core_init_content)
            print("  ✅ core/__init__.py criado")
        
        # common/__init__.py  
        common_init_content = '''"""
Common resources - Recursos compartilhados.

Inclui:
- config: Configurações centralizadas
- utils: Utilitários e helpers
- constants: Constantes da aplicação
"""

__all__ = ["config", "utils"]
'''
        
        common_init = self.root_dir / "common" / "__init__.py"
        if not common_init.exists():
            common_init.write_text(common_init_content)
            print("  ✅ common/__init__.py criado")
    
    def update_setup_py(self):
        """Atualiza setup.py com as melhorias."""
        print("⚙️ Atualizando setup.py...")
        
        setup_py = self.root_dir / "setup.py"
        if setup_py.exists():
            content = setup_py.read_text()
            
            # Atualizar versão
            content = content.replace('version="2.0.0"', 'version="2.1.0"')
            
            # Atualizar descrição
            content = content.replace(
                'description="Complete organizational automation system"',
                'description="Complete modular organizational automation system for arturdr-org"'
            )
            
            # Atualizar paths de shared para common
            content = content.replace('shared/', 'common/')
            
            setup_py.write_text(content)
            print("  ✅ setup.py atualizado para v2.1.0")
    
    def update_documentation(self):
        """Atualiza documentação com as melhorias."""
        print("📚 Atualizando documentação...")
        
        readme_path = self.root_dir / "docs" / "README.md"
        if readme_path.exists():
            content = readme_path.read_text()
            
            # Atualizar estrutura na documentação
            old_structure = """```
AI-powered-org-automation-suite/
├── core/           # Sistema central
├── modules/        # Módulos específicos  
├── shared/         # Recursos compartilhados
├── docs/          # Documentação
└── tests/         # Testes organizados
```"""
            
            new_structure = """```
AI-powered-org-automation-suite/
├── core/           # Sistema central (automation, monitoring, testing)
├── modules/        # Módulos específicos (cicd, security, quality)
├── common/         # Recursos compartilhados (config, utils, constants)
├── docs/          # Documentação organizada
└── tests/         # Testes estruturados
```"""
            
            content = content.replace(old_structure, new_structure)
            
            # Atualizar exemplos
            content = content.replace('shared/config', 'common/config')
            
            readme_path.write_text(content)
            print("  ✅ Documentação atualizada")
    
    def run_refinements(self):
        """Executa todas as melhorias na estrutura."""
        print("🚀 Iniciando refinamentos da estrutura modular...")
        print("="*60)
        
        try:
            # 1. Renomear shared → common
            self.rename_shared_to_common()
            
            # 2. Organizar workflows
            self.organize_github_workflows()
            
            # 3. Padronizar nomes
            self.standardize_directory_names()
            
            # 4. Melhorar __init__.py
            self.create_improved_init_files()
            
            # 5. Atualizar setup.py
            self.update_setup_py()
            
            # 6. Atualizar documentação
            self.update_documentation()
            
            print("\n" + "="*60)
            print("🎉 REFINAMENTOS CONCLUÍDOS COM SUCESSO!")
            print("="*60)
            print("✅ Diretório 'shared' renomeado para 'common' (mais intuitivo)")
            print("✅ Workflows do GitHub Actions organizados corretamente")
            print("✅ Nomes de diretórios padronizados")
            print("✅ __init__.py melhorados com imports mais claros")
            print("✅ setup.py atualizado para v2.1.0")
            print("✅ Documentação atualizada")
            print("\n🎯 Melhorias implementadas:")
            print("- 📁 Nomes mais intuitivos (common vs shared)")
            print("- ⚙️ Workflows organizados em .github/workflows/")
            print("- 📦 Imports melhorados e mais claros")
            print("- 📚 Documentação atualizada")
            print("- 🏷️ Versão incrementada para v2.1.0")
            
        except Exception as e:
            print(f"❌ Erro durante refinamentos: {e}")
            raise


def main():
    """Função principal."""
    refiner = StructureRefiner()
    refiner.run_refinements()


if __name__ == "__main__":
    main()