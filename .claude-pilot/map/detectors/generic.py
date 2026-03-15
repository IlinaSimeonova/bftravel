"""Universal fallback detector — works on any project."""

from pathlib import Path
from collections import Counter

from map.detectors.base import BaseDetector, DetectorResult
from core import walk_files, read_file_safe


class GenericDetector(BaseDetector):
    """Fallback detector that works on any codebase."""

    def detect(self) -> bool:
        return True  # always matches

    def analyze(self) -> DetectorResult:
        result = DetectorResult(framework="Generic")

        files = walk_files(self.root)
        ext_counts = Counter(f.suffix.lower() for f in files if f.suffix)

        # Detect primary language from file extensions
        lang_map = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".java": "Java",
            ".php": "PHP", ".cs": "C#", ".cpp": "C++", ".c": "C",
            ".swift": "Swift", ".kt": "Kotlin",
        }
        for ext, lang in lang_map.items():
            if ext_counts.get(ext, 0) > 0:
                result.language = lang
                break

        # Detect database from common files
        if (self.root / "docker-compose.yml").exists():
            content = read_file_safe(self.root / "docker-compose.yml")
            if "postgres" in content.lower():
                result.database = "PostgreSQL"
            elif "mysql" in content.lower():
                result.database = "MySQL"
            elif "mongo" in content.lower():
                result.database = "MongoDB"

        # Detect services from docker-compose
        if (self.root / "docker-compose.yml").exists():
            content = read_file_safe(self.root / "docker-compose.yml")
            for svc in ["redis", "elasticsearch", "rabbitmq", "kafka", "minio"]:
                if svc in content.lower():
                    result.services.append(svc.capitalize())

        # Detect env vars from .env.example
        for env_file in [".env.example", ".env.sample"]:
            path = self.root / env_file
            if path.exists():
                content = read_file_safe(path)
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        result.env_vars.append(line.split("=", 1)[0].strip())
                break

        # Common entry points
        for ep in ["main.py", "app.py", "server.py", "index.js", "index.ts", "main.go", "Makefile"]:
            if (self.root / ep).exists():
                result.entry_points.append(ep)

        return result
