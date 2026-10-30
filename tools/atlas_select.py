#!/usr/bin/env python3
"""Atlas Composition Selector (Tool Facade).

Backward-compatible entry point forwarding directly to the Atlas Runtime CLI.
Zero-dependency, Python 3.9+ standard library.
"""
import os
import sys

# Add atlas-skill to sys.path
ATLAS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ATLAS_ROOT not in sys.path:
    sys.path.insert(0, ATLAS_ROOT)

from runtime.cli import main

if __name__ == "__main__":
    sys.exit(main())

