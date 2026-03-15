"""Layer 5: Conventions — how does this project work?"""

import re
from pathlib import Path

from map.detectors.base import DetectorResult
from core import read_file_safe


def generate_conventions(root: Path, detector: DetectorResult) -> str:
    """Generate the Conventions section of the map."""
    lines = []

    # Testing
    test_info = _detect_testing(root)
    if test_info:
        lines.append(f"Tests: {test_info}")

    # Linting / formatting
    lint_info = _detect_linting(root)
    if lint_info:
        lines.append(f"Style: {lint_info}")

    # CI/CD
    ci_info = _detect_ci(root)
    if ci_info:
        lines.append(f"CI: {ci_info}")

    # Code patterns
    patterns = _detect_patterns(root, detector)
    if patterns:
        lines.append(f"Patterns: {', '.join(patterns)}")

    # Auth
    auth = _detect_auth(root, detector)
    if auth:
        lines.append(f"Auth: {auth}")

    # API style
    api = _detect_api_style(root, detector)
    if api:
        lines.append(f"API: {api}")

    return "\n".join(lines)


def _detect_testing(root: Path) -> str:
    """Detect test framework and configuration."""
    parts = []

    # pytest
    for cfg in ["pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini"]:
        path = root / cfg
        if path.exists():
            content = read_file_safe(path)
            if "[tool.pytest" in content or "[pytest]" in content:
                parts.append("pytest")
                break

    # Check for conftest.py as pytest indicator
    if not parts and (root / "conftest.py").exists():
        parts.append("pytest")

    # jest
    if (root / "jest.config.js").exists() or (root / "jest.config.ts").exists():
        parts.append("jest")
    elif (root / "package.json").exists():
        content = read_file_safe(root / "package.json")
        if '"jest"' in content:
            parts.append("jest")

    # Check for test directories/files existence
    has_tests = False
    for pattern in ["tests/", "test/", "**/tests.py", "**/test_*.py"]:
        if list(root.glob(pattern)):
            has_tests = True
            break

    if not parts and not has_tests:
        return "none detected"

    if parts:
        return ", ".join(parts)
    return "test files present (framework unclear)"


def _detect_linting(root: Path) -> str:
    """Detect linting and formatting tools."""
    tools = []

    tool_files = {
        ".flake8": "flake8",
        ".pylintrc": "pylint",
        "pyrightconfig.json": "pyright",
        ".prettierrc": "prettier",
        ".prettierrc.json": "prettier",
        ".prettierrc.yml": "prettier",
        ".eslintrc.js": "eslint",
        ".eslintrc.json": "eslint",
        "eslint.config.js": "eslint",
        "biome.json": "biome",
    }

    for fname, tool in tool_files.items():
        if (root / fname).exists():
            tools.append(tool)

    # Check pyproject.toml for tool configs
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        content = read_file_safe(pyproject)
        if "[tool.ruff" in content:
            tools.append("ruff")
        if "[tool.black" in content:
            tools.append("black")
        if "[tool.isort" in content:
            tools.append("isort")
        if "[tool.mypy" in content:
            tools.append("mypy")

    if not tools:
        return "none configured"

    return ", ".join(tools)


def _detect_ci(root: Path) -> str:
    """Detect CI/CD system."""
    systems = []

    if (root / ".github" / "workflows").is_dir():
        systems.append("GitHub Actions")
    if (root / ".gitlab-ci.yml").exists():
        systems.append("GitLab CI")
    if (root / "Jenkinsfile").exists():
        systems.append("Jenkins")
    if (root / ".circleci").is_dir():
        systems.append("CircleCI")
    if (root / ".travis.yml").exists():
        systems.append("Travis CI")
    if (root / "bitbucket-pipelines.yml").exists():
        systems.append("Bitbucket Pipelines")

    if not systems:
        return "none"

    return ", ".join(systems)


def _detect_patterns(root: Path, detector: DetectorResult) -> list[str]:
    """Detect coding patterns used in the project."""
    patterns = []

    if detector.framework == "Django":
        # Check view style
        for app in detector.apps:
            views_py = root / app.path / "views.py"
            if views_py.exists():
                content = read_file_safe(views_py, max_bytes=20_000)
                if re.search(r"^class \w+.*View", content, re.MULTILINE):
                    if "class-based views" not in patterns:
                        patterns.append("class-based views")
                if re.search(r"^def \w+\(request", content, re.MULTILINE):
                    if "function views" not in patterns:
                        patterns.append("function views")

        # Service layer
        for app in detector.apps:
            if (root / app.path / "services").is_dir():
                patterns.append("service layer")
                break

        # Form classes
        for app in detector.apps:
            if app.form_count > 0:
                patterns.append("form classes")
                break

    # Check for type hints
    py_files = list(root.glob("**/*.py"))[:10]
    type_hint_count = 0
    for f in py_files:
        content = read_file_safe(f, max_bytes=5000)
        if re.search(r"def \w+\([^)]*:\s*\w+", content):
            type_hint_count += 1
    if type_hint_count > 3:
        patterns.append("type hints")

    return patterns


def _detect_auth(root: Path, detector: DetectorResult) -> str:
    """Detect authentication approach."""
    if detector.extra.get("auth_user_model"):
        return f"custom user model ({detector.extra['auth_user_model']})"

    # Check for common auth packages
    for req_file in ["requirements.txt"]:
        path = root / req_file
        if path.exists():
            content = read_file_safe(path).lower()
            if "djangorestframework-simplejwt" in content:
                return "JWT (simplejwt)"
            if "django-allauth" in content:
                return "django-allauth"
            if "django-oauth-toolkit" in content:
                return "OAuth2"

    # Check for auth backend
    for app in detector.apps:
        backends = root / app.path / "backends.py"
        if backends.exists():
            return "custom auth backend"

    return ""


def _detect_api_style(root: Path, detector: DetectorResult) -> str:
    """Detect API patterns."""
    styles = []

    # DRF
    if "rest_framework" in detector.installed_apps:
        styles.append("Django REST Framework")

    # Check for API views
    for app in detector.apps:
        for fname in ["api_views.py", "api.py", "serializers.py"]:
            if (root / app.path / fname).exists():
                if "REST API" not in styles and "Django REST Framework" not in styles:
                    styles.append("REST API")
                break

    # GraphQL
    if "graphene_django" in detector.installed_apps:
        styles.append("GraphQL (Graphene)")

    # Channels/WebSocket
    if "channels" in detector.installed_apps:
        styles.append("WebSocket (Channels)")

    if not styles:
        return ""
    return ", ".join(styles)
