"""IndexReader — loads and queries .claude-pilot/index.json."""

import json
from pathlib import Path
from typing import Optional


class IndexReader:
    """Reads and queries the claude-pilot index."""

    def __init__(self, root: Path):
        self.root = root
        self._data: Optional[dict] = None

    @property
    def data(self) -> dict:
        if self._data is None:
            self._data = self._load()
        return self._data

    def reload(self):
        """Force reload from disk."""
        self._data = self._load()

    def _load(self) -> dict:
        index_path = self.root / ".claude-pilot" / "index.json"
        if not index_path.exists():
            return {"version": 1, "files": {}, "modules": {}, "symbols": {}}
        try:
            return json.loads(index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"version": 1, "files": {}, "modules": {}, "symbols": {}}

    def get_file_info(self, path: str) -> Optional[dict]:
        """Get indexed info about a specific file."""
        return self.data.get("files", {}).get(path)

    def get_module_files(self, module: str) -> list[str]:
        """Get all files in a top-level module."""
        return self.data.get("modules", {}).get(module, [])

    def find_symbol(self, name: str) -> list[str]:
        """Find files containing a symbol (class/function)."""
        return self.data.get("symbols", {}).get(name, [])

    def get_importers(self, module_path: str) -> list[str]:
        """Find files that import from the given module."""
        # Normalize to module notation
        module_name = module_path.replace("/", ".").replace(".py", "")
        if module_name.endswith(".__init__"):
            module_name = module_name[:-9]

        importers = []
        for path, info in self.data.get("files", {}).items():
            file_imports = info.get("imports", [])
            for imp in file_imports:
                if imp == module_name or imp.startswith(module_name + "."):
                    importers.append(path)
                    break
        return importers

    def get_dependencies(self, file_path: str) -> dict:
        """Get imports and reverse imports for a file."""
        info = self.get_file_info(file_path)
        imports = info.get("imports", []) if info else []
        importers = self.get_importers(file_path)
        return {
            "imports": imports,
            "imported_by": importers,
        }

    def search_files(self, query: str) -> list[str]:
        """Search file paths and symbols for a query string."""
        query_lower = query.lower()
        results = []

        # Search file paths
        for path in self.data.get("files", {}):
            if query_lower in path.lower():
                results.append(path)

        # Search symbols
        for symbol, paths in self.data.get("symbols", {}).items():
            if query_lower in symbol.lower():
                for p in paths:
                    if p not in results:
                        results.append(p)

        return results
