"""Git hook install/uninstall/dispatch."""

import os
import stat
import sys
from pathlib import Path


# Hook types we manage
HOOK_TYPES = ["pre-commit", "post-checkout", "post-merge"]

# Marker to identify our hook content
MARKER = "# CLAUDE-PILOT HOOK"

# Hook script template — runs directly, never blocks git
HOOK_TEMPLATE = """#!/bin/sh
{marker}
# Auto-installed by claude-pilot. Do not edit between markers.
python3 .claude-pilot/updater/hooks.py {hook_type} "$@" || true
# END CLAUDE-PILOT HOOK
"""


def install_hooks(root: Path) -> list[str]:
    """Install git hooks. Returns list of installed hook names.

    If a hook already exists, appends our content rather than overwriting.
    """
    hooks_dir = root / ".git" / "hooks"
    if not hooks_dir.is_dir():
        return []

    installed = []
    for hook_type in HOOK_TYPES:
        hook_path = hooks_dir / hook_type
        our_content = HOOK_TEMPLATE.format(marker=MARKER, hook_type=hook_type)

        if hook_path.exists():
            existing = hook_path.read_text(encoding="utf-8")
            if MARKER in existing:
                continue  # Already installed
            # Append to existing hook
            if not existing.endswith("\n"):
                existing += "\n"
            existing += "\n" + our_content.lstrip("#!/bin/sh\n")
            hook_path.write_text(existing, encoding="utf-8")
        else:
            hook_path.write_text(our_content, encoding="utf-8")

        # Make executable
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
        installed.append(hook_type)

    return installed


def uninstall_hooks(root: Path):
    """Remove claude-pilot content from git hooks."""
    hooks_dir = root / ".git" / "hooks"
    if not hooks_dir.is_dir():
        return

    for hook_type in HOOK_TYPES:
        hook_path = hooks_dir / hook_type
        if not hook_path.exists():
            continue

        content = hook_path.read_text(encoding="utf-8")
        if MARKER not in content:
            continue

        # Remove our section
        lines = content.splitlines()
        new_lines = []
        skip = False
        for line in lines:
            if MARKER in line:
                skip = True
                continue
            if skip and "END CLAUDE-PILOT HOOK" in line:
                skip = False
                continue
            if not skip:
                new_lines.append(line)

        new_content = "\n".join(new_lines).strip()
        if new_content and new_content != "#!/bin/sh":
            hook_path.write_text(new_content + "\n", encoding="utf-8")
        else:
            # Hook is now empty, remove it
            hook_path.unlink()


def check_hooks(root: Path) -> list[str]:
    """Check which hooks are installed. Returns list of hook names."""
    hooks_dir = root / ".git" / "hooks"
    if not hooks_dir.is_dir():
        return []

    installed = []
    for hook_type in HOOK_TYPES:
        hook_path = hooks_dir / hook_type
        if hook_path.exists():
            content = hook_path.read_text(encoding="utf-8")
            if MARKER in content:
                installed.append(hook_type)

    return installed


def dispatch(hook_type: str, args: list[str]):
    """Dispatch a hook invocation to the appropriate handler."""
    # Ensure .claude-pilot is on sys.path
    _pkg_root = str(Path(__file__).resolve().parent.parent)
    if _pkg_root not in sys.path:
        sys.path.insert(0, _pkg_root)

    from updater.incremental import incremental_refresh
    from updater.full import full_refresh

    # Find project root
    from core import git_root
    root = git_root(".")
    if not root:
        return

    map_file = root / ".claude-pilot" / "map.md"
    if not map_file.exists():
        return  # Not initialized

    if hook_type == "pre-commit":
        # Quick: update activity and stage the map into the commit
        incremental_refresh(root)
        import subprocess
        subprocess.run(
            ["git", "add", ".claude-pilot/map.md"],
            cwd=str(root), timeout=5,
        )

    elif hook_type in ("post-checkout", "post-merge"):
        # Heavier: full refresh
        full_refresh(root)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        dispatch(sys.argv[1], sys.argv[2:])
