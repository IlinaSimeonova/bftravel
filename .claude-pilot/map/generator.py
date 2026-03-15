"""Orchestrates framework detection + all 5 layers → map string."""

import sys
from pathlib import Path

# Ensure .claude-pilot is on sys.path for absolute imports
_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from map.detectors import detect_framework
from map.layers.identity import generate_identity
from map.layers.structure import generate_structure
from map.layers.relationships import generate_relationships
from map.layers.activity import generate_activity
from map.layers.conventions import generate_conventions
from map.renderer import render_map


def generate_map(root: Path) -> str:
    """Generate the full project map.

    Returns the map as a markdown string.
    """
    # Detect framework and get deep analysis
    detector_result = detect_framework(root)

    # Infer project name from directory or config
    project_name = _infer_project_name(root, detector_result)

    # Generate all 5 layers
    identity = generate_identity(root, detector_result)
    structure = generate_structure(root, detector_result)
    relationships = generate_relationships(root, detector_result)
    activity = generate_activity(root)
    conventions = generate_conventions(root, detector_result)

    return render_map(
        project_name=project_name,
        identity=identity,
        structure=structure,
        relationships=relationships,
        activity=activity,
        conventions=conventions,
    )


def generate_activity_only(root: Path) -> str:
    """Quick refresh: regenerate only the activity section."""
    return generate_activity(root)


def _infer_project_name(root: Path, detector) -> str:
    """Try to find a human-readable project name."""
    # Detector's own inference wins (e.g. Django settings docstring, README)
    if detector.extra.get("project_name"):
        name = detector.extra["project_name"]
        # Only use if it looks like a real project name, not a tool name
        if name != root.name:
            return name

    # Check package.json
    pkg = root / "package.json"
    if pkg.exists():
        import json
        try:
            data = json.loads(pkg.read_text())
            if data.get("name"):
                return data["name"]
        except (json.JSONDecodeError, OSError):
            pass

    # Check pyproject.toml for project name
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            for line in content.splitlines():
                if line.strip().startswith("name"):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        return parts[1].strip().strip('"').strip("'")
        except OSError:
            pass

    # Fall back to directory name
    return root.name.replace("-", " ").replace("_", " ").title()
