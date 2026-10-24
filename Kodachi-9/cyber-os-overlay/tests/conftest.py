"""Pytest configuration and fixtures."""

import os
import sys
import tempfile
from pathlib import Path

overlay_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(overlay_root))
os.environ["CYBER_OS_LOG_DIR"] = tempfile.mkdtemp(prefix="cyber-os-tests-")
