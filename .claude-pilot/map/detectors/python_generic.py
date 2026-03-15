"""Generic Python detector — Flask, FastAPI, plain Python."""

import re
from pathlib import Path

from map.detectors.base import BaseDetector, DetectorResult
from core import read_file_safe, walk_files


class PythonGenericDetector(BaseDetector):
    """Detects non-Django Python projects (Flask, FastAPI, etc.)."""

    def detect(self) -> bool:
        # Must have Python files but NOT be Django
        has_python = False
        for f in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]:
            if (self.root / f).exists():
                content = read_file_safe(self.root / f)
                if "django" in content.lower():
                    return False  # Let Django detector handle it
                has_python = True

        if not has_python:
            # Check for Python files directly
            py_files = list(self.root.glob("*.py"))
            has_python = len(py_files) > 0

        return has_python

    def analyze(self) -> DetectorResult:
        result = DetectorResult(language="Python")

        # Detect framework
        result.framework = self._detect_framework()
        result.framework_version = self._detect_version(result.framework)
        result.language_version = self._detect_python_version()

        # Database
        result.database = self._detect_database()

        # Services
        result.services = self._detect_services()

        # Entry points
        result.entry_points = self._find_entry_points()

        # Env vars
        result.env_vars = self._detect_env_vars()

        return result

    def _detect_framework(self) -> str:
        reqs = self._read_requirements()

        if "fastapi" in reqs:
            return "FastAPI"
        if "flask" in reqs:
            return "Flask"
        if "starlette" in reqs:
            return "Starlette"
        if "tornado" in reqs:
            return "Tornado"
        if "aiohttp" in reqs:
            return "aiohttp"

        # Check main files for framework imports
        for f in ["app.py", "main.py", "server.py"]:
            path = self.root / f
            if path.exists():
                content = read_file_safe(path)
                if "FastAPI" in content:
                    return "FastAPI"
                if "Flask" in content:
                    return "Flask"

        return "Python"

    def _read_requirements(self) -> str:
        """Read all requirements into one lowercase string."""
        parts = []
        for f in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]:
            path = self.root / f
            if path.exists():
                parts.append(read_file_safe(path).lower())
        return "\n".join(parts)

    def _detect_version(self, framework: str) -> str:
        reqs = self._read_requirements()
        fw_lower = framework.lower()
        for line in reqs.splitlines():
            if fw_lower in line and ("==" in line or ">=" in line):
                match = re.search(r"[>=<]+\s*([\d.]+)", line)
                if match:
                    return match.group(1)
        return ""

    def _detect_python_version(self) -> str:
        pv = self.root / ".python-version"
        if pv.exists():
            return read_file_safe(pv).strip()

        pyproject = self.root / "pyproject.toml"
        if pyproject.exists():
            content = read_file_safe(pyproject)
            match = re.search(r'requires-python\s*=\s*["\']([^"\']+)', content)
            if match:
                return match.group(1)
        return ""

    def _detect_database(self) -> str:
        reqs = self._read_requirements()
        if "psycopg" in reqs:
            return "PostgreSQL"
        if "pymysql" in reqs or "mysqlclient" in reqs:
            return "MySQL"
        if "pymongo" in reqs:
            return "MongoDB"
        if "sqlalchemy" in reqs:
            return "SQLAlchemy (DB engine varies)"
        return ""

    def _detect_services(self) -> list[str]:
        reqs = self._read_requirements()
        services = []
        markers = {
            "redis": "Redis", "celery": "Celery", "boto3": "AWS",
            "anthropic": "Anthropic Claude", "openai": "OpenAI",
            "stripe": "Stripe", "sentry": "Sentry",
        }
        for marker, name in markers.items():
            if marker in reqs:
                services.append(name)
        return services

    def _find_entry_points(self) -> list[str]:
        eps = []
        for f in ["main.py", "app.py", "server.py", "run.py", "cli.py", "Makefile"]:
            if (self.root / f).exists():
                eps.append(f)
        return eps

    def _detect_env_vars(self) -> list[str]:
        env_vars = set()
        for env_file in [".env.example", ".env.sample"]:
            path = self.root / env_file
            if path.exists():
                for line in read_file_safe(path).splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        env_vars.add(line.split("=", 1)[0].strip())
        return sorted(env_vars)
