#!/usr/bin/env python3
# Compatibility layer - redirects to modular structure
import sys
from pathlib import Path

# Add core module to path
sys.path.insert(0, str(Path(__file__).parent / "core"))

from automation.main import *

if __name__ == "__main__":
    from automation.main import main
    main()
