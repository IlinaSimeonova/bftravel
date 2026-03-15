"""FastMCP server with 5 navigator tools."""

import ast
import re
import subprocess
import sys
from pathlib import Path

# Ensure .claude-pilot is on sys.path for absolute imports
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from core import git_root, git_cmd, read_file_safe

# Lazy-load mcp to keep it optional
_mcp = None
_index = None
_root = None


def _get_root() -> Path:
    global _root
    if _root is None:
        _root = git_root(".") or Path.cwd()
    return _root


def _get_index():
    global _index
    if _index is None:
        from navigator.index import IndexReader
        _index = IndexReader(_get_root())
    return _index


def create_server():
    """Create and configure the MCP server."""
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("Claude-Pilot Navigator")
    root = _get_root()

    @mcp.tool()
    def get_module_context(path: str) -> str:
        """Get a focused briefing on a specific file or directory.

        Returns: what this module does, its dependencies, reverse dependencies,
        recent changes, key classes/functions, and TODOs.
        """
        idx = _get_index()
        target = root / path
        lines = []

        if target.is_dir():
            # Directory briefing
            lines.append(f"# Module: {path}")

            # List key files
            module_name = path.rstrip("/").split("/")[0]
            files = idx.get_module_files(module_name)
            # Filter to those under the requested path
            matching = [f for f in files if f.startswith(path.rstrip("/"))]

            if matching:
                lines.append(f"\nFiles ({len(matching)}):")
                for f in sorted(matching)[:30]:
                    info = idx.get_file_info(f)
                    symbols = info.get("symbols", []) if info else []
                    if symbols:
                        lines.append(f"  {f}: {', '.join(symbols[:5])}")
                    else:
                        lines.append(f"  {f}")

        elif target.is_file():
            # File briefing
            lines.append(f"# File: {path}")

            content = read_file_safe(target, max_bytes=50_000)
            if target.suffix == ".py" and content:
                # Extract classes and functions with signatures
                try:
                    tree = ast.parse(content)
                    for node in ast.iter_child_nodes(tree):
                        if isinstance(node, ast.ClassDef):
                            bases = [_name(b) for b in node.bases]
                            lines.append(f"\nclass {node.name}({', '.join(bases)})")
                            # Show methods
                            for item in node.body:
                                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                    sig = _func_sig(item)
                                    lines.append(f"  def {sig}")
                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            sig = _func_sig(node)
                            lines.append(f"\ndef {sig}")
                except SyntaxError:
                    pass

            # Dependencies
            info = idx.get_file_info(path)
            if info:
                imports = info.get("imports", [])
                if imports:
                    lines.append(f"\nImports: {', '.join(imports[:15])}")

            # Reverse deps
            importers = idx.get_importers(path)
            if importers:
                lines.append(f"Imported by: {', '.join(importers[:10])}")

            # TODOs
            if content:
                todos = re.findall(r"#\s*(TODO|FIXME|HACK|XXX):?\s*(.+)", content)
                if todos:
                    lines.append("\nTODOs:")
                    for kind, msg in todos[:5]:
                        lines.append(f"  {kind}: {msg.strip()}")

            # Recent git changes
            log = git_cmd(
                ["log", "-5", "--oneline", "--", path],
                cwd=str(root), timeout=5,
            )
            if log:
                lines.append(f"\nRecent changes:\n{log}")

        else:
            return f"Path not found: {path}"

        return "\n".join(lines)

    @mcp.tool()
    def get_recent_changes(scope: str = "", days: int = 7) -> str:
        """Get structured change history, optionally scoped to a directory.

        Args:
            scope: Directory to filter changes to (empty = entire project)
            days: Number of days to look back (default 7)
        """
        args = [
            "log", f"--since={days} days ago",
            "--format=%h|%s|%an|%ar",
            "--stat",
        ]
        if scope:
            args.extend(["--", scope])

        raw = git_cmd(args, cwd=str(root), timeout=15)
        if not raw:
            return "No changes found."

        # Parse and format
        lines = ["# Recent Changes"]
        if scope:
            lines.append(f"Scope: {scope} | Last {days} days\n")
        else:
            lines.append(f"Last {days} days\n")

        # Summarize: count files changed per area
        lines.append(raw[:3000])  # Cap output

        return "\n".join(lines)

    @mcp.tool()
    def get_dependencies(file: str) -> str:
        """Get import graph in both directions for a file.

        Returns what this file imports and what imports this file.
        """
        idx = _get_index()
        deps = idx.get_dependencies(file)

        lines = [f"# Dependencies: {file}"]

        imports = deps.get("imports", [])
        if imports:
            lines.append(f"\nImports ({len(imports)}):")
            for imp in sorted(imports):
                lines.append(f"  {imp}")
        else:
            lines.append("\nNo imports found.")

        imported_by = deps.get("imported_by", [])
        if imported_by:
            lines.append(f"\nImported by ({len(imported_by)}):")
            for imp in sorted(imported_by):
                lines.append(f"  {imp}")
        else:
            lines.append("\nNot imported by any indexed file.")

        return "\n".join(lines)

    @mcp.tool()
    def get_patterns(type: str) -> str:
        """Get 2-3 examples of a code pattern from this project.

        Args:
            type: Pattern type — e.g. "view", "model", "test", "form",
                  "serializer", "task", "api_endpoint", "management_command"
        """
        idx = _get_index()

        # Map pattern types to file/symbol patterns
        pattern_map = {
            "view": {"files": ["views.py", "api_views.py"], "pattern": r"^(def \w+\(request|class \w+.*View)"},
            "model": {"files": ["models.py"], "pattern": r"^class \w+\(.*Model"},
            "form": {"files": ["forms.py"], "pattern": r"^class \w+\(.*Form"},
            "test": {"files": ["test_*.py", "tests.py"], "pattern": r"^(class Test|def test_)"},
            "serializer": {"files": ["serializers.py"], "pattern": r"^class \w+.*Serializer"},
            "task": {"files": ["tasks.py"], "pattern": r"^@.*task|^def \w+"},
            "api_endpoint": {"files": ["api_views.py", "api.py"], "pattern": r"^(def \w+|class \w+)"},
            "management_command": {"files": ["management/commands/*.py"], "pattern": r"^class Command"},
            "middleware": {"files": ["middleware.py", "middleware/*.py"], "pattern": r"^class \w+"},
            "admin": {"files": ["admin.py"], "pattern": r"^class \w+.*Admin|@admin"},
        }

        config = pattern_map.get(type, {"files": [f"*{type}*"], "pattern": r"^(class|def) \w+"})

        lines = [f"# Pattern examples: {type}"]
        examples_found = 0

        # Search for matching files
        for file_pattern in config["files"]:
            matches = list(root.glob(f"**/{file_pattern}"))
            for match in matches[:5]:
                if examples_found >= 3:
                    break

                rel = match.relative_to(root)
                content = read_file_safe(match, max_bytes=20_000)
                if not content:
                    continue

                # Find matching code blocks
                snippets = _extract_snippets(content, config["pattern"])
                if snippets:
                    for snippet in snippets[:1]:
                        examples_found += 1
                        lines.append(f"\n## {rel}")
                        lines.append(f"```python\n{snippet}\n```")

        if examples_found == 0:
            lines.append(f"\nNo examples of '{type}' found in the project.")

        return "\n".join(lines)

    @mcp.tool()
    def search_context(query: str) -> str:
        """Search the codebase for a keyword and return matches with context.

        Returns matching files and relevant code snippets.
        """
        idx = _get_index()

        lines = [f"# Search: {query}"]

        # Search index first
        index_matches = idx.search_files(query)
        if index_matches:
            lines.append(f"\nIndex matches ({len(index_matches)}):")
            for m in index_matches[:10]:
                lines.append(f"  {m}")

        # Grep the codebase
        try:
            result = subprocess.run(
                ["grep", "-rn", "--include=*.py", "--include=*.js", "--include=*.ts",
                 "--include=*.html", "--include=*.md",
                 "-l", query, str(root)],
                capture_output=True, text=True, timeout=10,
            )
            if result.stdout:
                grep_files = result.stdout.strip().splitlines()
                # Show relative paths
                grep_rel = []
                for f in grep_files[:15]:
                    try:
                        grep_rel.append(str(Path(f).relative_to(root)))
                    except ValueError:
                        grep_rel.append(f)

                lines.append(f"\nGrep matches ({len(grep_files)} files):")
                for f in grep_rel:
                    lines.append(f"  {f}")

                # Show context from first 3 files
                for f in grep_files[:3]:
                    try:
                        ctx_result = subprocess.run(
                            ["grep", "-n", "-C2", query, f],
                            capture_output=True, text=True, timeout=5,
                        )
                        if ctx_result.stdout:
                            rel = str(Path(f).relative_to(root))
                            lines.append(f"\n## {rel}")
                            # Cap output per file
                            lines.append(ctx_result.stdout[:1000])
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        pass

        except (subprocess.TimeoutExpired, FileNotFoundError):
            lines.append("\nGrep search unavailable.")

        return "\n".join(lines)

    return mcp


def _name(node) -> str:
    """Get name from an AST node."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_name(node.value)}.{node.attr}"
    return "?"


def _func_sig(node) -> str:
    """Get function signature string from AST node."""
    args = []
    for arg in node.args.args:
        name = arg.arg
        if arg.annotation:
            name += f": {_name(arg.annotation)}"
        args.append(name)
    return f"{node.name}({', '.join(args)})"


def _extract_snippets(content: str, pattern: str, max_lines: int = 15) -> list[str]:
    """Extract code snippets matching a pattern."""
    snippets = []
    lines = content.splitlines()

    for i, line in enumerate(lines):
        if re.match(pattern, line):
            # Grab the definition + some body
            end = min(i + max_lines, len(lines))
            # Find end of block (next definition or blank line after content)
            for j in range(i + 1, end):
                if j < len(lines) and re.match(r"^(class |def |async def )", lines[j]):
                    end = j
                    break
            snippet = "\n".join(lines[i:end])
            snippets.append(snippet)

    return snippets


def main():
    """Run the MCP server."""
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
