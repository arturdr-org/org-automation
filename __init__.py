"""
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
