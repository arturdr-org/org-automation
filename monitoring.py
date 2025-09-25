#!/usr/bin/env python3
# Compatibility layer - redirects to modular structure
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "core"))

from monitoring.health_check import *

if __name__ == "__main__":
    from monitoring.health_check import main
    main()
