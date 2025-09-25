#!/usr/bin/env python3
"""
Script de Migração para Estrutura Modular
Reorganiza o org-automation de forma segura mantendo compatibilidade.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List

class ModularMigration:
    """Gerencia a migração para estrutura modular."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.backup_dir = self.root_dir / "backup_pre_migration"
        
        # Mapeamento de arquivos para nova estrutura
        self.migration_map = {
            # Core automation
            "enhanced_automation.py": "core/automation/main.py",
            "automa_org.py": "core/automation/legacy.py",
            
            # Monitoring
            "monitoring.py": "core/monitoring/health_check.py", 
            "dashboard.py": "core/monitoring/dashboard.py",
            
            # Testing
            "test_setup.py": "core/testing/setup_validator.py",
            
            # CI/CD Templates
            "workflow-templates/python-ci.yml": "modules/cicd/templates/python-ci.yml",
            "workflow-templates/nodejs-ci.yml": "modules/cicd/templates/nodejs-ci.yml", 
            "workflow-templates/release-automation.yml": "modules/cicd/templates/release-automation.yml",
            
            # Shared configs
            "config/labels.yml": "shared/config/labels.yml",
            "config/branch_protection.yml": "shared/config/branch_protection.yml",
            "config/CODEOWNERS": "shared/config/CODEOWNERS",
            "config/templates/": "shared/config/templates/",
            
            # Documentation
            "README.md": "docs/README.md",
            "SETUP.md": "docs/SETUP.md", 
            "GOVERNANCE.md": "docs/GOVERNANCE.md",
            "COMPLETION_SUMMARY.md": "docs/COMPLETION_SUMMARY.md"
        }
    
    def create_backup(self):
        """Cria backup completo antes da migração."""
        print("📦 Criando backup...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Clonar repositório atual
        subprocess.run([
            "git", "clone", ".", str(self.backup_dir)
        ], check=True)
        
        print(f"✅ Backup criado em: {self.backup_dir}")
    
    def create_modular_structure(self):
        """Cria a estrutura de pastas modular."""
        print("🏗️ Criando estrutura modular...")
        
        directories = [
            # Core
            "core/automation",
            "core/monitoring", 
            "core/testing",
            
            # Modules
            "modules/cicd/templates",
            "modules/security",
            "modules/quality", 
            "modules/notifications",
            
            # Shared
            "shared/config/templates",
            "shared/utils",
            
            # GitHub workflows
            ".github/workflows", 
            
            # Documentation
            "docs/modules",
            
            # Tests
            "tests/unit",
            "tests/integration", 
            "tests/fixtures",
            
            # Scripts
            "scripts"
        ]
        
        for directory in directories:
            dir_path = self.root_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Criar __init__.py para packages Python
            if any(dir_name in directory for dir_name in ["core", "modules", "shared", "tests"]):
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text('"""Package module."""\n')
        
        print("✅ Estrutura modular criada")
    
    def migrate_files(self):
        """Move arquivos para nova estrutura."""
        print("📁 Migrando arquivos...")
        
        for old_path, new_path in self.migration_map.items():
            old_file = self.root_dir / old_path
            new_file = self.root_dir / new_path
            
            if old_file.exists():
                # Criar diretório pai se não existir
                new_file.parent.mkdir(parents=True, exist_ok=True)
                
                if old_file.is_dir():
                    if new_file.exists():
                        shutil.rmtree(new_file)
                    shutil.copytree(old_file, new_file)
                else:
                    shutil.copy2(old_file, new_file)
                
                print(f"  📄 {old_path} → {new_path}")
        
        print("✅ Arquivos migrados")
    
    def create_compatibility_layer(self):
        """Cria camada de compatibilidade para não quebrar imports."""
        print("🔗 Criando camada de compatibilidade...")
        
        compatibility_files = {
            "enhanced_automation.py": """#!/usr/bin/env python3
# Compatibility layer - redirects to modular structure
import sys
from pathlib import Path

# Add core module to path
sys.path.insert(0, str(Path(__file__).parent / "core"))

from automation.main import *

if __name__ == "__main__":
    from automation.main import main
    main()
""",
            "monitoring.py": """#!/usr/bin/env python3
# Compatibility layer - redirects to modular structure
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "core"))

from monitoring.health_check import *

if __name__ == "__main__":
    from monitoring.health_check import main
    main()
""",
            "dashboard.py": """#!/usr/bin/env python3
# Compatibility layer - redirects to modular structure
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "core"))

from monitoring.dashboard import *

if __name__ == "__main__":
    from monitoring.dashboard import main
    main()
"""
        }
        
        for filename, content in compatibility_files.items():
            compat_file = self.root_dir / filename
            compat_file.write_text(content)
            print(f"  🔗 Criado: {filename}")
        
        print("✅ Camada de compatibilidade criada")
    
    def create_main_package_init(self):
        """Cria __init__.py principal para importações fáceis."""
        print("📦 Configurando package principal...")
        
        init_content = '''"""
org-automation: Sistema completo de automação organizacional

Módulos disponíveis:
- core: Funcionalidades centrais (automation, monitoring, testing)
- modules: Módulos específicos (cicd, security, quality, notifications)  
- shared: Recursos compartilhados (config, utils)
"""

__version__ = "2.0.0"
__author__ = "arturdr-org"

# Importações principais para facilitar uso
from core.automation.main import OrganizationAutomation
from core.monitoring.health_check import OrganizationHealthMonitor
from core.monitoring.dashboard import OrganizationDashboard

__all__ = [
    "OrganizationAutomation",
    "OrganizationHealthMonitor", 
    "OrganizationDashboard"
]
'''
        
        init_file = self.root_dir / "__init__.py"
        init_file.write_text(init_content)
        print("✅ Package principal configurado")
    
    def update_imports(self):
        """Atualiza imports nos arquivos migrados."""
        print("🔄 Atualizando imports...")
        
        # Arquivos que precisam de ajuste de imports
        files_to_update = [
            self.root_dir / "core/automation/main.py",
            self.root_dir / "core/monitoring/health_check.py",
            self.root_dir / "core/monitoring/dashboard.py"
        ]
        
        for file_path in files_to_update:
            if file_path.exists():
                content = file_path.read_text()
                
                # Atualizar paths para shared configs
                content = content.replace(
                    'Path(__file__).parent / "config"',
                    'Path(__file__).parent.parent.parent / "shared/config"'
                )
                content = content.replace(
                    'CONFIG_DIR = Path(__file__).parent / "config"',
                    'CONFIG_DIR = Path(__file__).parent.parent.parent / "shared/config"'
                )
                content = content.replace(
                    'TEMPLATES_DIR = CONFIG_DIR / "templates"',
                    'TEMPLATES_DIR = CONFIG_DIR / "templates"'
                )
                
                file_path.write_text(content)
                print(f"  🔄 Atualizado: {file_path.name}")
        
        print("✅ Imports atualizados")
    
    def create_setup_py(self):
        """Cria setup.py para instalação como package."""
        print("📄 Criando setup.py...")
        
        setup_content = '''#!/usr/bin/env python3
"""Setup script for org-automation package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "docs" / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="org-automation",
    version="2.0.0",
    author="arturdr-org",
    description="Complete organizational automation system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "org-automation=core.automation.main:main",
            "org-monitor=core.monitoring.health_check:main", 
            "org-dashboard=core.monitoring.dashboard:main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
'''
        
        setup_file = self.root_dir / "setup.py"
        setup_file.write_text(setup_content)
        print("✅ setup.py criado")
    
    def update_documentation(self):
        """Atualiza documentação para refletir nova estrutura."""
        print("📚 Atualizando documentação...")
        
        readme_path = self.root_dir / "docs" / "README.md"
        if readme_path.exists():
            content = readme_path.read_text()
            
            # Adicionar seção sobre nova estrutura
            modular_section = """

## 🏗️ Nova Estrutura Modular

O sistema foi reorganizado em uma arquitetura modular para melhor manutenibilidade:

```
org-automation/
├── core/           # Sistema central
├── modules/        # Módulos específicos  
├── shared/         # Recursos compartilhados
├── docs/          # Documentação
└── tests/         # Testes organizados
```

### 📦 Como Usar a Nova Estrutura

```python
# Importação direta
from core.automation.main import OrganizationAutomation
from core.monitoring.dashboard import OrganizationDashboard

# Via package principal
import org_automation
automation = org_automation.OrganizationAutomation()
```

### 🔗 Compatibilidade

Os scripts antigos continuam funcionando:
```bash
python enhanced_automation.py  # → core/automation/main.py
python monitoring.py          # → core/monitoring/health_check.py
python dashboard.py           # → core/monitoring/dashboard.py
```

"""
            
            # Inserir antes das referências se existirem
            if "## 📚 Referências" in content:
                content = content.replace("## 📚 Referências", modular_section + "\n## 📚 Referências")
            else:
                content += modular_section
            
            readme_path.write_text(content)
            print("  📚 README.md atualizado")
        
        print("✅ Documentação atualizada")
    
    def run_migration(self):
        """Executa migração completa."""
        print("🚀 Iniciando migração para estrutura modular...")
        
        try:
            self.create_backup()
            self.create_modular_structure()
            self.migrate_files()
            self.update_imports()
            self.create_compatibility_layer()
            self.create_main_package_init()
            self.create_setup_py()
            self.update_documentation()
            
            print("\n" + "="*60)
            print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("="*60)
            print("✅ Backup criado em: backup_pre_migration/")
            print("✅ Nova estrutura modular implementada")
            print("✅ Compatibilidade mantida com scripts antigos")
            print("✅ Package Python configurado")
            print("✅ Documentação atualizada")
            print("\n🔄 Próximos passos:")
            print("1. Testar scripts antigos para garantir compatibilidade")
            print("2. Executar testes com nova estrutura")
            print("3. Commit das mudanças")
            print("4. Considerar deprecar scripts antigos gradualmente")
            
        except Exception as e:
            print(f"❌ Erro durante migração: {e}")
            print("🔄 Restaure o backup se necessário")
            raise


def main():
    """Função principal."""
    migrator = ModularMigration()
    migrator.run_migration()


if __name__ == "__main__":
    main()