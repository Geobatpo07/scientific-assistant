"""Tesla - Multi-agent scientific assistant for applied mathematics and data science."""

__version__ = "0.2.0"
__author__ = "Geobatpo07"

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
