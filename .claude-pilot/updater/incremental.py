"""Post-commit: activity-only refresh (<2s target)."""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure .claude-pilot is on sys.path for absolute imports
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from map.layers.activity import generate_activity


def incremental_refresh(root: Path):
    """Update only the Activity section of the map. Fast (<2s)."""
    map_path = root / ".claude-pilot" / "map.md"
    if not map_path.exists():
        return

    content = map_path.read_text(encoding="utf-8")
    new_activity = generate_activity(root)

    # Replace activity section
    content = _replace_section(content, "Activity", new_activity)

    # Update timestamp
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    content = re.sub(r"Generated: .+", f"Generated: {ts}", content)

    map_path.write_text(content, encoding="utf-8")


def _replace_section(content: str, section_name: str, new_content: str) -> str:
    """Replace a ## Section in the map with new content."""
    pattern = rf"(## {section_name}\n).*?(?=\n## |\Z)"
    return re.sub(pattern, rf"\1{new_content}", content, flags=re.DOTALL)
