"""Layer 3: Relationships — what connects to what?"""

import ast
import re
from pathlib import Path
from collections import defaultdict

from map.detectors.base import DetectorResult
from core import walk_files, read_file_safe


def generate_relationships(root: Path, detector: DetectorResult) -> str:
    """Generate the Relationships section of the map."""
    lines = []

    # Build import graph for key files
    imports = _build_import_graph(root)

    # Show inter-module dependencies
    if imports:
        # Group by top-level module
        module_deps = _module_level_deps(imports)
        if module_deps:
            lines.append("Module dependencies:")
            for mod, deps in sorted(module_deps.items()):
                if deps:
                    lines.append(f"  {mod} → {', '.join(sorted(deps))}")

    # Entry points (from detector)
    if detector.entry_points:
        lines.append(f"Entry points: {', '.join(detector.entry_points)}")

    # URL routing summary (Django-specific)
    if detector.extra.get("root_urlconf"):
        url_summary = _parse_url_routes(root, detector.extra["root_urlconf"])
        if url_summary:
            lines.append("URL routes:")
            for route in url_summary:
                lines.append(f"  {route}")

    # External connections (services)
    if detector.services:
        lines.append(f"External services: {', '.join(detector.services)}")

    # Model relationships (Django)
    if detector.framework == "Django":
        model_rels = _trace_model_relationships(root, detector)
        if model_rels:
            lines.append("Model relationships:")
            for rel in model_rels[:15]:
                lines.append(f"  {rel}")

    return "\n".join(lines)


def _build_import_graph(root: Path) -> dict[str, set[str]]:
    """Build a simplified import graph from Python files."""
    graph = defaultdict(set)
    py_files = [f for f in walk_files(root) if f.suffix == ".py"]

    for rel_path in py_files[:200]:  # Cap to prevent slowness
        abs_path = root / rel_path
        content = read_file_safe(abs_path, max_bytes=50_000)
        if not content:
            continue

        module = str(rel_path).replace("/", ".").replace(".py", "")
        if module.endswith(".__init__"):
            module = module[:-9]

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    graph[module].add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:
                    graph[module].add(node.module.split(".")[0])
                elif node.level > 0 and node.module:
                    # Relative import — resolve
                    parts = module.split(".")
                    if len(parts) >= node.level:
                        base = ".".join(parts[:len(parts) - node.level + 1])
                        graph[module].add(base.split(".")[0])

    return graph


def _module_level_deps(imports: dict[str, set[str]]) -> dict[str, set[str]]:
    """Aggregate imports to top-level module relationships."""
    # Get all top-level modules that are local (appear as keys)
    local_modules = {k.split(".")[0] for k in imports.keys()}

    module_deps = defaultdict(set)
    for source, targets in imports.items():
        src_mod = source.split(".")[0]
        for target in targets:
            target_mod = target.split(".")[0]
            if target_mod in local_modules and target_mod != src_mod:
                module_deps[src_mod].add(target_mod)

    return dict(module_deps)


def _parse_url_routes(root: Path, root_urlconf: str) -> list[str]:
    """Parse Django URL configuration to show route summary."""
    url_file = root / (root_urlconf.replace(".", "/") + ".py")
    if not url_file.exists():
        # Try as urls.py in the module dir
        parts = root_urlconf.replace(".", "/").rsplit("/", 1)
        url_file = root / parts[0] / "urls.py" if len(parts) > 1 else root / "urls.py"
        if not url_file.exists():
            return []

    content = read_file_safe(url_file)
    routes = []

    # Find include() calls
    for match in re.finditer(r"path\(['\"]([^'\"]*)['\"],\s*include\(['\"]([^'\"]+)", content):
        prefix, included = match.group(1), match.group(2)
        routes.append(f"/{prefix} → {included}")

    # Find direct view references
    for match in re.finditer(
        r"path\(['\"]([^'\"]*)['\"],\s*(?:views\.)?(\w+)",
        content,
    ):
        prefix, view = match.group(1), match.group(2)
        if view not in ("include",):
            routes.append(f"/{prefix} → {view}")

    return routes[:15]


def _trace_model_relationships(root: Path, detector: DetectorResult) -> list[str]:
    """Find FK/M2M relationships between Django models."""
    rels = []

    for app in detector.apps:
        models_py = root / app.path / "models.py"
        if not models_py.exists():
            continue

        content = read_file_safe(models_py)
        current_model = None

        for line in content.splitlines():
            # Track current class
            class_match = re.match(r"class (\w+)\(", line)
            if class_match:
                current_model = class_match.group(1)
                continue

            if current_model:
                # ForeignKey
                fk_match = re.search(r"ForeignKey\(['\"]?(\w+)", line.strip())
                if fk_match:
                    target = fk_match.group(1)
                    if target != "self":
                        rels.append(f"{current_model} → {target} (FK)")

                # ManyToManyField
                m2m_match = re.search(r"ManyToManyField\(['\"]?(\w+)", line.strip())
                if m2m_match:
                    target = m2m_match.group(1)
                    rels.append(f"{current_model} ↔ {target} (M2M)")

                # OneToOneField
                o2o_match = re.search(r"OneToOneField\(['\"]?(\w+)", line.strip())
                if o2o_match:
                    target = o2o_match.group(1)
                    rels.append(f"{current_model} → {target} (1:1)")

    return rels
