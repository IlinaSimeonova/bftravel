"""CLI entry point: claude-pilot init, refresh, status, uninstall."""

import argparse
import json
import sys
import time
from pathlib import Path

# Ensure .claude-pilot is on sys.path for absolute imports
_pkg_root = str(Path(__file__).resolve().parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from __init__ import __version__
from core import git_root, ensure_cc_dir, cc_dir


def cmd_init(args):
    """Initialize claude-pilot in the current project."""
    root = git_root(args.path)
    if not root:
        print("Error: Not a git repository. Run from inside a git project.", file=sys.stderr)
        return 1

    print(f"Initializing Claude-Pilot in {root}")

    # 1. Generate map
    start = time.time()
    from map.generator import generate_map
    map_content = generate_map(root)
    elapsed = time.time() - start

    # 2. Write map
    out_dir = ensure_cc_dir(root)
    map_path = out_dir / "map.md"
    map_path.write_text(map_content, encoding="utf-8")
    print(f"  Map generated: .claude-pilot/map.md ({elapsed:.1f}s)")

    # 3. Build index
    from updater.full import build_index
    index = build_index(root)
    index_path = out_dir / "index.json"
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"  Index built: .claude-pilot/index.json ({len(index.get('files', {}))} files)")

    # 4. Write config
    config_path = out_dir / "config.json"
    if not config_path.exists():
        config_path.write_text(json.dumps({
            "version": __version__,
            "ignore_dirs": [],
            "ignore_files": [],
        }, indent=2), encoding="utf-8")
        print("  Config created: .claude-pilot/config.json")

    # 5. Install git hooks
    from updater.hooks import install_hooks
    installed = install_hooks(root)
    if installed:
        print(f"  Git hooks installed: {', '.join(installed)}")

    # 6. Inject into CLAUDE.md
    _inject_claude_md(root)

    # 7. Install mcp if needed, register MCP server
    _ensure_mcp_package()
    _register_mcp(root)

    # 8. Add .claude-pilot/index.json to .gitignore
    _ensure_gitignore(root)

    print("\nClaude-Pilot ready. Claude Code will now read .claude-pilot/map.md on every session.")
    return 0


def cmd_refresh(args):
    """Refresh the map."""
    root = git_root(args.path)
    if not root:
        print("Error: Not a git repository.", file=sys.stderr)
        return 1

    out_dir = cc_dir(root)
    if not (out_dir / "map.md").exists():
        print("Error: Claude-Pilot not initialized. Run 'python3 .claude-pilot/cli.py init' first.", file=sys.stderr)
        return 1

    start = time.time()

    if args.quick:
        # Quick refresh: activity only
        from map.layers.activity import generate_activity
        new_activity = generate_activity(root)

        map_path = out_dir / "map.md"
        if map_path.exists():
            content = map_path.read_text(encoding="utf-8")
            content = _replace_section(content, "Activity", new_activity)
            # Update timestamp
            import re
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            content = re.sub(r"Generated: .+", f"Generated: {ts}", content)
            map_path.write_text(content, encoding="utf-8")

        elapsed = time.time() - start
        print(f"Quick refresh done ({elapsed:.1f}s) — activity section updated")
    else:
        # Full refresh
        from map.generator import generate_map
        map_content = generate_map(root)
        (out_dir / "map.md").write_text(map_content, encoding="utf-8")

        # Rebuild index
        from updater.full import build_index
        index = build_index(root)
        (out_dir / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

        elapsed = time.time() - start
        print(f"Full refresh done ({elapsed:.1f}s)")

    return 0


def cmd_status(args):
    """Show claude-pilot status."""
    root = git_root(args.path)
    if not root:
        print("Error: Not a git repository.", file=sys.stderr)
        return 1

    out_dir = cc_dir(root)
    map_path = out_dir / "map.md"
    if not map_path.exists():
        print("Claude-Pilot: Not initialized (no map.md found)")
        print(f"  Run: python3 .claude-pilot/cli.py init")
        return 0
    index_path = out_dir / "index.json"

    print(f"Claude-Pilot status for {root.name}")

    if map_path.exists():
        import os
        mtime = map_path.stat().st_mtime
        from datetime import datetime
        age = datetime.now().timestamp() - mtime
        if age < 60:
            age_str = f"{int(age)}s ago"
        elif age < 3600:
            age_str = f"{int(age / 60)}m ago"
        elif age < 86400:
            age_str = f"{int(age / 3600)}h ago"
        else:
            age_str = f"{int(age / 86400)}d ago"
        size = map_path.stat().st_size
        print(f"  Map: {size:,} bytes, last updated {age_str}")
    else:
        print("  Map: missing")

    if index_path.exists():
        data = json.loads(index_path.read_text())
        file_count = len(data.get("files", {}))
        print(f"  Index: {file_count} files indexed")
    else:
        print("  Index: missing")

    # Check hooks
    from updater.hooks import check_hooks
    hooks = check_hooks(root)
    if hooks:
        print(f"  Hooks: {', '.join(hooks)}")
    else:
        print("  Hooks: not installed")

    # Check CLAUDE.md
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")
        if "@.claude-pilot/map.md" in content:
            print("  CLAUDE.md: map reference present")
        else:
            print("  CLAUDE.md: map reference MISSING")
    else:
        print("  CLAUDE.md: file not found")

    return 0


def cmd_uninstall(args):
    """Remove claude-pilot from the project."""
    root = git_root(args.path)
    if not root:
        print("Error: Not a git repository.", file=sys.stderr)
        return 1

    # Remove hooks
    from updater.hooks import uninstall_hooks
    uninstall_hooks(root)
    print("  Git hooks removed")

    # Remove generated files (not source code)
    d = cc_dir(root)
    for fname in ["map.md", "index.json", "config.json"]:
        f = d / fname
        if f.exists():
            f.unlink()
    print("  Generated files removed (map.md, index.json, config.json)")

    # Remove CLAUDE.md injection
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")
        new_content = content.replace("@.claude-pilot/map.md\n", "").replace("@.claude-pilot/map.md", "")
        if new_content != content:
            claude_md.write_text(new_content, encoding="utf-8")
            print("  CLAUDE.md reference removed")

    # Remove MCP registration
    mcp_json = root / ".mcp.json"
    if mcp_json.exists():
        try:
            data = json.loads(mcp_json.read_text())
            if "claude-pilot" in data.get("mcpServers", {}):
                del data["mcpServers"]["claude-pilot"]
                mcp_json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                print("  MCP server registration removed")
        except (json.JSONDecodeError, OSError):
            pass

    print("\nClaude-Pilot uninstalled.")
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _inject_claude_md(root: Path):
    """Add @.claude-pilot/map.md reference to CLAUDE.md."""
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")
        if "@.claude-pilot/map.md" in content:
            print("  CLAUDE.md already has map reference")
            return
        # Insert after the first heading
        lines = content.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_idx = i + 1
                break
        lines.insert(insert_idx, "@.claude-pilot/map.md")
        claude_md.write_text("\n".join(lines), encoding="utf-8")
        print("  CLAUDE.md updated with @.claude-pilot/map.md")
    else:
        claude_md.write_text("# CLAUDE.md\n@.claude-pilot/map.md\n", encoding="utf-8")
        print("  CLAUDE.md created with map reference")


def _ensure_mcp_package():
    """Install mcp package if not already available."""
    try:
        import mcp  # noqa: F401
        return
    except ImportError:
        pass
    print("  Installing mcp package...")
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "mcp"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode == 0:
        print("  mcp package installed")
    else:
        print(f"  Warning: failed to install mcp — Navigator MCP server won't work")
        print(f"  Run manually: pip install mcp")


def _register_mcp(root: Path):
    """Add claude-pilot navigator to .mcp.json."""
    mcp_json = root / ".mcp.json"
    if mcp_json.exists():
        try:
            data = json.loads(mcp_json.read_text())
        except json.JSONDecodeError:
            data = {"mcpServers": {}}
    else:
        data = {"mcpServers": {}}

    if "claude-pilot" in data.get("mcpServers", {}):
        print("  MCP server already registered")
        return

    data.setdefault("mcpServers", {})["claude-pilot"] = {
        "command": "python3",
        "args": [".claude-pilot/navigator/server.py"],
    }
    mcp_json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("  MCP server registered in .mcp.json")


def _ensure_gitignore(root: Path):
    """Add .claude-pilot/index.json to .gitignore (cache file, not the map)."""
    gitignore = root / ".gitignore"
    marker = ".claude-pilot/index.json"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if marker in content:
            return
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n# Claude-Pilot (index is a rebuild-able cache)\n{marker}\n"
        gitignore.write_text(content, encoding="utf-8")
        print("  .gitignore updated")
    else:
        gitignore.write_text(f"# Claude-Pilot (index is a rebuild-able cache)\n{marker}\n", encoding="utf-8")
        print("  .gitignore created")


def _replace_section(content: str, section_name: str, new_content: str) -> str:
    """Replace a ## Section in the map with new content."""
    import re
    pattern = rf"(## {section_name}\n).*?(?=\n## |\Z)"
    replacement = f"\\1{new_content}"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="claude-pilot",
        description="LLM-optimized codebase orientation for Claude Code",
    )
    parser.add_argument("--version", action="version", version=f"claude-pilot {__version__}")

    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="Initialize claude-pilot in current project")
    p_init.add_argument("--path", default=".", help="Project root path")

    # refresh
    p_refresh = sub.add_parser("refresh", help="Refresh the map")
    p_refresh.add_argument("--quick", action="store_true", help="Activity-only refresh")
    p_refresh.add_argument("--path", default=".", help="Project root path")

    # status
    p_status = sub.add_parser("status", help="Show claude-pilot status")
    p_status.add_argument("--path", default=".", help="Project root path")

    # uninstall
    p_uninstall = sub.add_parser("uninstall", help="Remove claude-pilot from project")
    p_uninstall.add_argument("--path", default=".", help="Project root path")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    cmds = {
        "init": cmd_init,
        "refresh": cmd_refresh,
        "status": cmd_status,
        "uninstall": cmd_uninstall,
    }
    return cmds[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
