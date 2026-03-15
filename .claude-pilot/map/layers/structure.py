"""Layer 2: Structure — where is everything?"""

import os
from pathlib import Path
from collections import Counter

from map.detectors.base import DetectorResult
from core import walk_files, SKIP_DIRS


def generate_structure(root: Path, detector: DetectorResult) -> str:
    """Generate the Structure section of the map."""
    lines = []

    # If detector found apps, show them first
    if detector.apps:
        for app in detector.apps:
            parts = [f"**{app.name}/** — {app.purpose}" if app.purpose else f"**{app.name}/**"]
            stats = []
            if app.model_count:
                stats.append(f"{app.model_count} models")
            if app.view_count:
                stats.append(f"{app.view_count} views")
            if app.form_count:
                stats.append(f"{app.form_count} forms")
            if app.template_count:
                stats.append(f"{app.template_count} templates")
            if app.has_admin:
                stats.append("admin")
            if app.has_tasks:
                stats.append("tasks")
            if app.management_commands:
                stats.append(f"commands: {', '.join(app.management_commands)}")
            if stats:
                parts[0] += f" ({', '.join(stats)})"
            if app.key_files:
                parts.append(f"  Key: {', '.join(app.key_files)}")
            lines.append("\n".join(parts))

    # Config directory
    if detector.config_dir:
        lines.append(f"**{detector.config_dir}/** — Configuration (settings, urls, routing)")

    # Templates
    if detector.template_dir:
        tpl_count = _count_files_in(root / detector.template_dir)
        lines.append(f"**{detector.template_dir}/** — Templates ({tpl_count} files)")

    # Static
    if detector.static_dir:
        lines.append(f"**{detector.static_dir}/** — Static files")

    # Show top-level directories not already covered
    covered = {
        app.path.rstrip("/").split("/")[0] for app in detector.apps
    }
    if detector.config_dir:
        covered.add(detector.config_dir.rstrip("/").split("/")[0])
    if detector.template_dir:
        covered.add(detector.template_dir.rstrip("/").split("/")[0])
    if detector.static_dir:
        covered.add(detector.static_dir.rstrip("/").split("/")[0])

    top_dirs = _get_top_level_dirs(root)
    other_dirs = []
    for d, info in top_dirs.items():
        if d in covered or d in SKIP_DIRS:
            continue
        other_dirs.append((d, info))

    if other_dirs:
        for dirname, info in other_dirs:
            annotation = _annotate_dir(root, dirname, info)
            lines.append(f"**{dirname}/** — {annotation}")

    # Show file count summary
    files = walk_files(root)
    ext_counts = Counter(f.suffix.lower() for f in files if f.suffix)
    top_exts = ext_counts.most_common(5)
    if top_exts:
        ext_str = ", ".join(f"{ext} ({count})" for ext, count in top_exts)
        lines.append(f"Files: {len(files)} total — {ext_str}")

    return "\n".join(lines)


def _get_top_level_dirs(root: Path) -> dict[str, dict]:
    """Get top-level directories with basic stats."""
    dirs = {}
    # Extra dirs to skip in map (build artifacts, temp, logs)
    extra_skip = {"_logs", "temp-png", "logs", "tmp", "temp"}
    try:
        for entry in sorted(root.iterdir()):
            if (entry.is_dir()
                and entry.name not in SKIP_DIRS
                and entry.name not in extra_skip
                and not entry.name.startswith(".")
                and not entry.name.endswith(".egg-info")):
                file_count = sum(1 for _ in entry.rglob("*") if _.is_file())
                dirs[entry.name] = {"file_count": file_count}
    except OSError:
        pass
    return dirs


def _count_files_in(path: Path) -> int:
    """Count files recursively in a directory."""
    if not path.exists():
        return 0
    try:
        return sum(1 for _ in path.rglob("*") if _.is_file())
    except OSError:
        return 0


def _annotate_dir(root: Path, dirname: str, info: dict) -> str:
    """Try to annotate a directory by its contents."""
    path = root / dirname
    fc = info.get("file_count", 0)

    # Common directory names → purpose
    annotations = {
        "tests": "Tests",
        "test": "Tests",
        "docs": "Documentation",
        "doc": "Documentation",
        "scripts": "Scripts",
        "bin": "Scripts/binaries",
        "lib": "Library code",
        "src": "Source code",
        "pkg": "Packages",
        "cmd": "Commands",
        "api": "API endpoints",
        "migrations": "Database migrations",
        "fixtures": "Test fixtures",
        "seeds": "Seed data",
        "content": "Content files",
        "prompts": "AI prompts",
        "specs": "Specifications",
        "services": "Service layer",
        "utils": "Utilities",
        "helpers": "Helper functions",
        "middleware": "Middleware",
        "tasks": "Background tasks",
        "management": "Management commands",
    }

    purpose = annotations.get(dirname.lower(), "")

    # Try to infer from file types
    if not purpose:
        try:
            exts = Counter(f.suffix.lower() for f in path.rglob("*") if f.is_file() and f.suffix)
            top = exts.most_common(1)
            if top:
                ext_map = {
                    ".md": "Markdown content",
                    ".html": "HTML templates",
                    ".yml": "Configuration",
                    ".yaml": "Configuration",
                    ".json": "Data/config",
                    ".sql": "SQL scripts",
                }
                purpose = ext_map.get(top[0][0], "")
        except OSError:
            pass

    if purpose:
        return f"{purpose} ({fc} files)"
    return f"{fc} files"
