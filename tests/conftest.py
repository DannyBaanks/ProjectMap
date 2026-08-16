"""conftest: raiz importable + fixture paths."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FIXTURES = ROOT / "fixtures"
SIMPLE = FIXTURES / "simple"
MULTILANG = FIXTURES / "multilang"
LINGUIST = FIXTURES / "linguist"
# MEOW-ENGINE como fixture "cabrón" (repo real que no controlamos). Apunta al
# repo clonado al lado de ProjectMap. Si no existe, tests de MEOW se skip.
MEOW = ROOT.parent / "MEOW-ENGINE"
