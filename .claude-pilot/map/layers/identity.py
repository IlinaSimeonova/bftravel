"""Layer 1: Identity — what is this project?"""

from pathlib import Path
from map.detectors.base import DetectorResult


def generate_identity(root: Path, detector: DetectorResult) -> str:
    """Generate the Identity section of the map."""
    parts = []

    # Main identity line
    identity_parts = []
    fw = detector.framework
    if detector.framework_version:
        fw += f" {detector.framework_version}"
    identity_parts.append(fw)

    lang = detector.language
    if detector.language_version:
        lang += f" {detector.language_version}"
    identity_parts.append(lang)

    if detector.database:
        identity_parts.append(f"DB: {detector.database}")
    if detector.port:
        identity_parts.append(f"Port: {detector.port}")

    parts.append(" | ".join(identity_parts))

    # Services
    if detector.services:
        parts.append(f"Services: {', '.join(detector.services)}")

    # Entry points
    if detector.entry_points:
        parts.append(f"Entry points: {', '.join(detector.entry_points)}")

    # Middleware (for web frameworks)
    if detector.middleware:
        parts.append(f"Middleware: {', '.join(detector.middleware)}")

    # Env vars (just names, not values)
    if detector.env_vars:
        # Show first 15, truncate
        vars_list = detector.env_vars[:15]
        line = f"Env vars: {', '.join(vars_list)}"
        if len(detector.env_vars) > 15:
            line += f" (+{len(detector.env_vars) - 15} more)"
        parts.append(line)

    return "\n".join(parts)
