"""Assembles map sections into final map.md markdown."""

from datetime import datetime, timezone


def render_map(
    project_name: str,
    identity: str,
    structure: str,
    relationships: str,
    activity: str,
    conventions: str,
) -> str:
    """Assemble all sections into the final map markdown."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    sections = [f"# Project Map — {project_name}", f"Generated: {ts}"]

    if identity:
        sections.append(f"\n## Identity\n{identity}")

    if structure:
        sections.append(f"\n## Structure\n{structure}")

    if relationships:
        sections.append(f"\n## Relationships\n{relationships}")

    if activity:
        sections.append(f"\n## Activity\n{activity}")

    if conventions:
        sections.append(f"\n## Conventions\n{conventions}")

    return "\n".join(sections) + "\n"
