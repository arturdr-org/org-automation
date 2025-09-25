"""
org-automation: Sistema completo de automação organizacional para arturdr-org

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
