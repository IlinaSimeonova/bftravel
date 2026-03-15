"""Layer 4: Activity — what's alive right now?"""

from pathlib import Path

from core import git_branch, git_log, git_status_short, git_files_changed_since


def generate_activity(root: Path) -> str:
    """Generate the Activity section of the map."""
    cwd = str(root)
    lines = []

    # Branch + uncommitted
    branch = git_branch(cwd)
    status = git_status_short(cwd)
    status_lines = [l for l in status.splitlines() if l.strip()] if status else []

    # Categorize uncommitted changes
    modified = sum(1 for l in status_lines if l[0:2].strip() in ("M", "MM"))
    new_files = sum(1 for l in status_lines if "?" in l[0:2] or l[0:2].strip() == "A")
    deleted = sum(1 for l in status_lines if l[0:2].strip() == "D")

    branch_line = f"Branch: {branch}" if branch else "Branch: (detached)"
    if status_lines:
        parts = []
        if modified:
            parts.append(f"{modified} modified")
        if new_files:
            parts.append(f"{new_files} new")
        if deleted:
            parts.append(f"{deleted} deleted")
        branch_line += f" | Uncommitted: {', '.join(parts)}"
    else:
        branch_line += " | Clean working tree"
    lines.append(branch_line)

    # Hot files (last 7 days)
    hot = git_files_changed_since(days=7, cwd=cwd)
    if hot:
        top_hot = hot[:8]
        hot_parts = [f"{path} ({count})" for path, count in top_hot]
        lines.append(f"Hot files (7d): {', '.join(hot_parts)}")

    # Recent commits (grouped by area)
    commits = git_log(cwd, count=20)
    if commits:
        # Show last 10 as compact list
        lines.append("Recent commits:")
        for c in commits[:10]:
            lines.append(f"  {c['hash']} {c['subject']} ({c['relative_date']})")
        if len(commits) > 10:
            lines.append(f"  ... +{len(commits) - 10} more")

    return "\n".join(lines)
