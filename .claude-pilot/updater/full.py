"""Full map + index rebuild."""

import ast
import json
import re
import sys
from pathlib import Path

# Ensure .claude-pilot is on sys.path for absolute imports
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from core import walk_files, read_file_safe, ensure_cc_dir
from map.generator import generate_map


def full_refresh(root: Path):
    """Full map regeneration + index rebuild."""
    out_dir = ensure_cc_dir(root)

    # Regenerate map
    map_content = generate_map(root)
    (out_dir / "map.md").write_text(map_content, encoding="utf-8")

    # Rebuild index
    index = build_index(root)
    (out_dir / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")


def build_index(root: Path) -> dict:
    """Build the navigator's cached index.

    The index contains:
    - files: path → {type, symbols, imports, size}
    - modules: top-level module → [files]
    - symbols: symbol → [file paths]
    """
    files_index = {}
    module_index = {}
    symbol_index = {}

    all_files = walk_files(root)

    for rel_path in all_files:
        abs_path = root / rel_path
        path_str = str(rel_path)

        entry = {
            "type": _file_type(rel_path),
        }

        # Index Python files more deeply
        if rel_path.suffix == ".py":
            content = read_file_safe(abs_path, max_bytes=100_000)
            if content:
                symbols = _extract_symbols(content)
                imports = _extract_imports(content)
                entry["symbols"] = symbols
                entry["imports"] = imports

                # Add to symbol index
                for sym in symbols:
                    symbol_index.setdefault(sym, []).append(path_str)

        # Add to module index
        top_module = str(rel_path).split("/")[0]
        module_index.setdefault(top_module, []).append(path_str)

        files_index[path_str] = entry

    return {
        "version": 1,
        "files": files_index,
        "modules": module_index,
        "symbols": symbol_index,
    }


def _file_type(path: Path) -> str:
    """Categorize a file by its extension and name."""
    name = path.name.lower()
    suffix = path.suffix.lower()

    type_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "jsx",
        ".tsx": "tsx",
        ".html": "template",
        ".css": "style",
        ".scss": "style",
        ".json": "config",
        ".yml": "config",
        ".yaml": "config",
        ".toml": "config",
        ".md": "docs",
        ".txt": "text",
        ".sh": "script",
        ".sql": "sql",
    }

    # Special names
    if name in ("dockerfile", "docker-compose.yml", "docker-compose.yaml"):
        return "docker"
    if name in ("makefile", "justfile"):
        return "build"
    if "test" in name or "spec" in name:
        return "test"
    if "migration" in str(path):
        return "migration"

    return type_map.get(suffix, "other")


def _extract_symbols(content: str) -> list[str]:
    """Extract class and function names from Python source."""
    symbols = []
    try:
        tree = ast.parse(content)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append(node.name)
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                symbols.append(node.name)
    except SyntaxError:
        # Fallback to regex
        symbols = re.findall(r"^(?:class|def|async def)\s+(\w+)", content, re.MULTILINE)

    return symbols


def _extract_imports(content: str) -> list[str]:
    """Extract import module names from Python source."""
    imports = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except SyntaxError:
        pass
    return imports
