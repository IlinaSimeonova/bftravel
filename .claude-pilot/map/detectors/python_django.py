"""Django deep detector — AST-based settings/models/urls parsing."""

import ast
import re
from pathlib import Path

from map.detectors.base import BaseDetector, DetectorResult, AppInfo
from core import read_file_safe, walk_files


class DjangoDetector(BaseDetector):
    """Detects Django projects and performs deep analysis via AST."""

    def detect(self) -> bool:
        """Check if this is a Django project."""
        # Check manage.py
        if (self.root / "manage.py").exists():
            content = read_file_safe(self.root / "manage.py")
            if "django" in content.lower() or "DJANGO_SETTINGS_MODULE" in content:
                return True

        # Check requirements
        for req_file in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]:
            path = self.root / req_file
            if path.exists():
                content = read_file_safe(path)
                if "django" in content.lower():
                    return True

        return False

    def analyze(self) -> DetectorResult:
        result = DetectorResult(
            framework="Django",
            language="Python",
        )

        # Find settings module
        settings_path = self._find_settings()
        if settings_path:
            self._parse_settings(settings_path, result)

        # Detect Python version
        result.language_version = self._detect_python_version()

        # Detect Django version
        result.framework_version = self._detect_django_version()

        # Discover and analyze apps
        result.apps = self._discover_apps(result)

        # Find config directory
        result.config_dir = self._find_config_dir()

        # Find template directory
        result.template_dir = self._find_template_dir()

        # Entry points
        result.entry_points = self._find_entry_points()

        # Detect services from requirements/settings
        result.services = self._detect_services()

        # Detect env vars
        result.env_vars = self._detect_env_vars()

        # Project name
        result.extra["project_name"] = self._infer_project_name()

        return result

    def _find_settings(self) -> Path | None:
        """Find the Django settings file."""
        # Check manage.py for DJANGO_SETTINGS_MODULE
        manage = self.root / "manage.py"
        if manage.exists():
            content = read_file_safe(manage)
            match = re.search(r"DJANGO_SETTINGS_MODULE['\"],\s*['\"]([^'\"]+)", content)
            if match:
                module = match.group(1)
                path = self.root / (module.replace(".", "/") + ".py")
                if path.exists():
                    return path
                # Try as package
                path = self.root / module.replace(".", "/") / "settings.py"
                if path.exists():
                    return path

        # Common patterns
        for pattern in [
            "config/settings.py",
            "settings.py",
            "*/settings.py",
            "config/settings/base.py",
        ]:
            matches = list(self.root.glob(pattern))
            if matches:
                return matches[0]

        return None

    def _parse_settings(self, path: Path, result: DetectorResult):
        """Parse settings.py using AST to extract key configuration."""
        content = read_file_safe(path)
        if not content:
            return

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue

            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue
                name = target.id

                if name == "INSTALLED_APPS":
                    result.installed_apps = self._extract_string_list(node.value)

                elif name == "MIDDLEWARE":
                    mw_list = self._extract_string_list(node.value)
                    # Simplify middleware names
                    result.middleware = [
                        m.rsplit(".", 1)[-1] for m in mw_list
                    ]

                elif name == "DATABASES":
                    result.database = self._extract_database(node.value)

                elif name == "ROOT_URLCONF":
                    if isinstance(node.value, ast.Constant):
                        result.extra["root_urlconf"] = node.value.value

                elif name == "AUTH_USER_MODEL":
                    if isinstance(node.value, ast.Constant):
                        result.extra["auth_user_model"] = node.value.value

                elif name == "DEFAULT_AUTO_FIELD":
                    pass  # not interesting for map

        # Detect port from settings or default
        result.port = "8000"  # Django default

        # Detect database from env if not found in AST
        if not result.database:
            if "DATABASE_URL" in content or "dj_database_url" in content:
                result.database = "PostgreSQL (via DATABASE_URL)"
            elif "psycopg2" in content or "'postgresql'" in content:
                result.database = "PostgreSQL"

    def _extract_string_list(self, node) -> list[str]:
        """Extract a list of strings from an AST node."""
        strings = []
        if isinstance(node, ast.List):
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    strings.append(elt.value)
        return strings

    def _extract_database(self, node) -> str:
        """Try to determine database engine from DATABASES setting."""
        # Walk the AST looking for ENGINE value
        for child in ast.walk(node):
            if isinstance(child, ast.Constant) and isinstance(child.value, str):
                val = child.value.lower()
                if "postgresql" in val or "psycopg2" in val:
                    return "PostgreSQL"
                elif "mysql" in val:
                    return "MySQL"
                elif "sqlite" in val:
                    return "SQLite"
                elif "oracle" in val:
                    return "Oracle"
        return ""

    def _detect_python_version(self) -> str:
        """Try to detect Python version from config files."""
        # Check pyproject.toml
        pyproject = self.root / "pyproject.toml"
        if pyproject.exists():
            content = read_file_safe(pyproject)
            match = re.search(r'requires-python\s*=\s*["\']([^"\']+)', content)
            if match:
                return match.group(1)

        # Check .python-version
        pv = self.root / ".python-version"
        if pv.exists():
            return read_file_safe(pv).strip()

        # Check runtime.txt
        rt = self.root / "runtime.txt"
        if rt.exists():
            content = read_file_safe(rt).strip()
            if content.startswith("python-"):
                return content.replace("python-", "")

        return ""

    def _detect_django_version(self) -> str:
        """Detect Django version from requirements."""
        for req_file in ["requirements.txt", "requirements/base.txt"]:
            path = self.root / req_file
            if path.exists():
                content = read_file_safe(path)
                for line in content.splitlines():
                    line = line.strip().lower()
                    if line.startswith("django") and ("==" in line or ">=" in line):
                        match = re.search(r"[>=<]+\s*([\d.]+)", line)
                        if match:
                            return match.group(1) + "+"
        return ""

    def _discover_apps(self, result: DetectorResult) -> list[AppInfo]:
        """Find and analyze Django apps."""
        apps = []

        # Get custom apps from INSTALLED_APPS (filter Django/third-party)
        custom_apps = []
        for app in result.installed_apps:
            if app.startswith("django.") or app in (
                "daphne", "channels", "rest_framework", "corsheaders",
                "debug_toolbar", "django_extensions", "celery",
            ):
                continue
            # Check if it's a local app directory
            app_dir = self.root / app.replace(".", "/")
            if app_dir.is_dir():
                custom_apps.append((app, app_dir))

        for app_name, app_dir in custom_apps:
            info = self._analyze_app(app_name, app_dir)
            apps.append(info)

        return apps

    def _analyze_app(self, name: str, app_dir: Path) -> AppInfo:
        """Deep-analyze a single Django app."""
        info = AppInfo(name=name, path=str(app_dir.relative_to(self.root)))

        # Count models
        models_py = app_dir / "models.py"
        if models_py.exists():
            info.model_count = self._count_classes(models_py, base_pattern=r"models\.Model")
            info.key_files.append("models.py")

        # Count views
        views_py = app_dir / "views.py"
        if views_py.exists():
            content = read_file_safe(views_py)
            # Count def-based views and class-based views
            info.view_count = len(re.findall(r"^def \w+\(request", content, re.MULTILINE))
            info.view_count += len(re.findall(r"^class \w+.*View", content, re.MULTILINE))
            info.key_files.append("views.py")

        # Count forms
        forms_py = app_dir / "forms.py"
        if forms_py.exists():
            info.form_count = self._count_classes(forms_py, base_pattern=r"forms\.\w+Form")
            info.key_files.append("forms.py")

        # Check for admin
        admin_py = app_dir / "admin.py"
        if admin_py.exists():
            content = read_file_safe(admin_py)
            info.has_admin = "admin.site.register" in content or "@admin.register" in content
            if info.has_admin:
                info.key_files.append("admin.py")

        # Check for tasks
        tasks_py = app_dir / "tasks.py"
        if tasks_py.exists():
            info.has_tasks = True
            info.key_files.append("tasks.py")

        # Check for tests
        if (app_dir / "tests.py").exists() or (app_dir / "tests").is_dir():
            info.has_tests = True

        # Management commands
        cmd_dir = app_dir / "management" / "commands"
        if cmd_dir.is_dir():
            info.management_commands = [
                f.stem for f in cmd_dir.glob("*.py")
                if f.stem != "__init__"
            ]

        # Check services directory
        svc_dir = app_dir / "services"
        if svc_dir.is_dir():
            svc_files = [f.stem for f in svc_dir.glob("*.py") if f.stem != "__init__"]
            if svc_files:
                info.key_files.append(f"services/ ({', '.join(svc_files)})")

        # Count templates for this app
        for tpl_dir in [self.root / "templates" / name, app_dir / "templates" / name]:
            if tpl_dir.is_dir():
                info.template_count = sum(
                    1 for _ in tpl_dir.rglob("*.html")
                )
                break

        # Try to infer purpose from models
        if info.model_count > 0:
            info.purpose = self._infer_app_purpose(app_dir)

        return info

    def _count_classes(self, path: Path, base_pattern: str = "") -> int:
        """Count class definitions in a Python file, optionally matching base class."""
        content = read_file_safe(path)
        if base_pattern:
            return len(re.findall(rf"^class \w+\(.*{base_pattern}", content, re.MULTILINE))
        return len(re.findall(r"^class \w+", content, re.MULTILINE))

    def _infer_app_purpose(self, app_dir: Path) -> str:
        """Try to infer what an app does from its models and views."""
        models_py = app_dir / "models.py"
        if not models_py.exists():
            return ""

        content = read_file_safe(models_py)
        model_names = re.findall(r"^class (\w+)\(", content, re.MULTILINE)
        if model_names:
            # Return first 5 model names as summary
            names = model_names[:5]
            summary = ", ".join(names)
            if len(model_names) > 5:
                summary += f" +{len(model_names) - 5} more"
            return summary
        return ""

    def _find_config_dir(self) -> str:
        """Find the Django config/project directory."""
        for name in ["config", "project", "core"]:
            path = self.root / name
            if path.is_dir() and (path / "settings.py").exists():
                return name
            if path.is_dir() and (path / "urls.py").exists():
                return name
        return ""

    def _find_template_dir(self) -> str:
        """Find the templates directory."""
        if (self.root / "templates").is_dir():
            return "templates"
        return ""

    def _find_entry_points(self) -> list[str]:
        """Find main entry points."""
        eps = []
        if (self.root / "manage.py").exists():
            eps.append("manage.py")
        config_dir = self._find_config_dir()
        if config_dir:
            if (self.root / config_dir / "urls.py").exists():
                eps.append(f"{config_dir}/urls.py")
            if (self.root / config_dir / "asgi.py").exists():
                eps.append(f"{config_dir}/asgi.py")
        if (self.root / "mcp_server.py").exists():
            eps.append("mcp_server.py")
        return eps

    def _detect_services(self) -> list[str]:
        """Detect external services from requirements and settings."""
        services = []
        seen = set()

        # Check requirements
        for req_file in ["requirements.txt", "requirements/base.txt"]:
            path = self.root / req_file
            if not path.exists():
                continue
            content = read_file_safe(path).lower()

            service_markers = {
                "redis": "Redis",
                "celery": "Celery",
                "channels-redis": "Redis (Channels)",
                "elasticsearch": "Elasticsearch",
                "boto3": "AWS (boto3)",
                "django-storages": "Cloud Storage",
                "sentry-sdk": "Sentry",
                "stripe": "Stripe",
                "anthropic": "Anthropic Claude",
                "openai": "OpenAI",
                "apify": "Apify",
                "sib-api": "Brevo/Sendinblue",
                "daphne": "Daphne (ASGI)",
            }

            for marker, name in service_markers.items():
                if marker in content and name not in seen:
                    services.append(name)
                    seen.add(name)

        return services

    def _detect_env_vars(self) -> list[str]:
        """Detect environment variables from .env files and settings."""
        env_vars = set()

        # From .env.example
        for env_file in [".env.example", ".env.sample"]:
            path = self.root / env_file
            if path.exists():
                content = read_file_safe(path)
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        env_vars.add(line.split("=", 1)[0].strip())

        # From settings.py — os.environ.get() calls
        settings = self._find_settings()
        if settings:
            content = read_file_safe(settings)
            for match in re.finditer(r"os\.environ\.get\(['\"](\w+)", content):
                env_vars.add(match.group(1))
            for match in re.finditer(r"os\.environ\[['\"](\w+)", content):
                env_vars.add(match.group(1))

        return sorted(env_vars)

    def _infer_project_name(self) -> str:
        """Try to infer the project name."""
        # Check settings for a project name hint
        settings = self._find_settings()
        if settings:
            content = read_file_safe(settings)
            # Look for docstring
            match = re.search(r'"""([^"]+)"""', content)
            if match:
                name = match.group(1).strip()
                if "settings" in name.lower():
                    # "Django settings for X" → extract X
                    match2 = re.search(r"for\s+(.+?)\.?\s*$", name)
                    if match2:
                        return match2.group(1).strip()
                return name

        # Check README
        readme = self.root / "README.md"
        if readme.exists():
            content = read_file_safe(readme)
            for line in content.splitlines():
                if line.startswith("# "):
                    return line[2:].strip()

        return self.root.name
