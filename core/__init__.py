"""
Core modules - Sistema central da automação organizacional.

Módulos:
- automation: Sistema principal de automação
- monitoring: Health checks e dashboard
- testing: Validação e testes
"""

from . import automation, monitoring, testing

__all__ = ["automation", "monitoring", "testing"]
