"""Simple tool registry loader

Expects providers YAML under integrations/tool-registry/providers/*.yaml
Each provider lists tools with fields: id, name, executable, category, description
"""
import os
import yaml
import shutil
from typing import List, Dict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROVIDERS_DIR = os.path.join(ROOT, "integrations", "tool-registry", "providers")


class ToolRegistry:
    def __init__(self, providers_dir: str = PROVIDERS_DIR):
        self.providers_dir = providers_dir
        self.providers = {}
        self._load_providers()

    def _load_providers(self):
        self.providers = {}
        if not os.path.isdir(self.providers_dir):
            raise FileNotFoundError(f"Providers dir not found: {self.providers_dir}")
        for fname in os.listdir(self.providers_dir):
            if not fname.endswith(".yaml") and not fname.endswith(".yml"):
                continue
            path = os.path.join(self.providers_dir, fname)
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
                self.providers[fname] = data

    def discover(self) -> List[Dict]:
        """Return list of tools with availability info (executable exists)
        """
        results = []
        for fname, pdata in self.providers.items():
            tools = pdata.get("tools", [])
            for t in tools:
                exec_name = t.get("executable")
                available = shutil.which(exec_name) is not None if exec_name else False
                entry = {
                    "id": t.get("id"),
                    "name": t.get("name"),
                    "executable": exec_name,
                    "available": available,
                    "category": t.get("category"),
                    "source_file": fname,
                }
                results.append(entry)
        return results

    def reload(self):
        self._load_providers()
