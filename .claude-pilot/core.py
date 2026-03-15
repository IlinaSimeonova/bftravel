"""Shared utilities: git commands, file walking, path helpers."""

import os
import subprocess
from pathlib import Path
from typing import Optional


def git_root(path: str = ".") -> Optional[Path]:
    """Find the git repository root from the given path."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=path, timeout=5,
        )
        if out.returncode == 0:
            return Path(out.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def git_cmd(args: list[str], cwd: str = ".", timeout: int = 10) -> str:
    """Run a git command and return stdout. Returns empty string on failure."""
    try:
        out = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, cwd=cwd, timeout=timeout,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def git_branch(cwd: str = ".") -> str:
    """Get current branch name."""
    return git_cmd(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)


def git_log(cwd: str = ".", count: int = 20, format_str: str = "%h|%s|%an|%ar|%D") -> list[dict]:
    """Get recent commits as structured dicts."""
    raw = git_cmd(
        ["log", f"-{count}", f"--format={format_str}", "--no-merges"],
        cwd=cwd, timeout=15,
    )
    if not raw:
        return []
    commits = []
    for line in raw.splitlines():
        parts = line.split("|", 4)
        if len(parts) >= 4:
            commits.append({
                "hash": parts[0],
                "subject": parts[1],
                "author": parts[2],
                "relative_date": parts[3],
                "refs": parts[4] if len(parts) > 4 else "",
            })
    return commits


def git_diff_stat(cwd: str = ".", staged: bool = False) -> str:
    """Get diff stat (file changes summary)."""
    args = ["diff", "--stat"]
    if staged:
        args.append("--cached")
    return git_cmd(args, cwd=cwd)


def git_status_short(cwd: str = ".") -> str:
    """Get short git status."""
    return git_cmd(["status", "--short"], cwd=cwd)


def git_files_changed_since(days: int = 7, cwd: str = ".") -> list[tuple[int, str]]:
    """Get files changed in last N days with change count, sorted by frequency."""
    raw = git_cmd(
        ["log", f"--since={days} days ago", "--name-only", "--format="],
        cwd=cwd, timeout=15,
    )
    if not raw:
        return []
    counts: dict[str, int] = {}
    for line in raw.splitlines():
        line = line.strip()
        if line:
            counts[line] = counts.get(line, 0) + 1
    return sorted(counts.items(), key=lambda x: -x[1])


# ---------------------------------------------------------------------------
# File walking
# ---------------------------------------------------------------------------

# Directories always skipped
SKIP_DIRS = {
    ".git", ".cc", "__pycache__", "node_modules", ".venv", "venv", "env",
    ".env", ".tox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "dist", "build", "egg-info", ".eggs", "staticfiles", "media",
    ".next", ".nuxt", ".svelte-kit", "coverage", ".nyc_output",
    ".idea", ".vscode", ".DS_Store",
}

# File extensions to skip
SKIP_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".o", ".a", ".dylib",
    ".jpg", ".jpeg", ".png", ".gif", ".ico", ".svg", ".webp",
    ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".tar", ".gz", ".bz2",
    ".db", ".sqlite3", ".sqlite",
    ".log", ".pid", ".lock",
}


def walk_files(root: Path, max_files: int = 5000) -> list[Path]:
    """Walk project files, skipping irrelevant dirs/files. Returns relative paths."""
    files = []
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skipped directories in-place
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.endswith(".egg-info")
        ]
        rel_dir = Path(dirpath).relative_to(root)
        for fname in filenames:
            if len(files) >= max_files:
                return files
            ext = Path(fname).suffix.lower()
            if ext in SKIP_EXTENSIONS or fname.startswith("."):
                continue
            files.append(rel_dir / fname)
    return files


def read_file_safe(path: Path, max_bytes: int = 100_000) -> str:
    """Read a file, returning empty string on any error."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return text[:max_bytes]
    except (OSError, UnicodeDecodeError):
        return ""


def cc_dir(root: Path) -> Path:
    """Return the .claude-pilot output directory path for a project root."""
    return root / ".claude-pilot"


def ensure_cc_dir(root: Path) -> Path:
    """Ensure .claude-pilot directory exists."""
    d = cc_dir(root)
    d.mkdir(exist_ok=True)
    return d
