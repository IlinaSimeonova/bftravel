"""Node.js/Express/Next.js detector — package.json parsing."""

import json
from pathlib import Path

from map.detectors.base import BaseDetector, DetectorResult
from core import read_file_safe


class NodeDetector(BaseDetector):
    """Detects Node.js projects from package.json."""

    def detect(self) -> bool:
        return (self.root / "package.json").exists()

    def analyze(self) -> DetectorResult:
        result = DetectorResult(language="JavaScript")

        pkg_data = self._read_package_json()
        if not pkg_data:
            return result

        # Detect TypeScript
        deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
        if "typescript" in deps:
            result.language = "TypeScript"

        # Detect framework
        result.framework, result.framework_version = self._detect_framework(deps)

        # Node version
        engines = pkg_data.get("engines", {})
        if "node" in engines:
            result.language_version = f"Node {engines['node']}"

        # Port
        scripts = pkg_data.get("scripts", {})
        start_cmd = scripts.get("start", "") + scripts.get("dev", "")
        if "--port" in start_cmd:
            import re
            match = re.search(r"--port\s+(\d+)", start_cmd)
            if match:
                result.port = match.group(1)
        elif result.framework == "Next.js":
            result.port = "3000"
        else:
            result.port = "3000"

        # Database
        result.database = self._detect_database(deps)

        # Services
        result.services = self._detect_services(deps)

        # Entry points
        result.entry_points = self._find_entry_points(pkg_data)

        # Env vars
        result.env_vars = self._detect_env_vars()

        # Project name
        result.extra["project_name"] = pkg_data.get("name", self.root.name)

        return result

    def _read_package_json(self) -> dict:
        try:
            return json.loads(read_file_safe(self.root / "package.json"))
        except json.JSONDecodeError:
            return {}

    def _detect_framework(self, deps: dict) -> tuple[str, str]:
        frameworks = [
            ("next", "Next.js"),
            ("nuxt", "Nuxt.js"),
            ("@sveltejs/kit", "SvelteKit"),
            ("svelte", "Svelte"),
            ("@angular/core", "Angular"),
            ("vue", "Vue.js"),
            ("react", "React"),
            ("express", "Express"),
            ("fastify", "Fastify"),
            ("hono", "Hono"),
            ("koa", "Koa"),
            ("nestjs", "NestJS"),
        ]
        for pkg, name in frameworks:
            if pkg in deps:
                version = deps[pkg].lstrip("^~>=")
                return name, version
        return "Node.js", ""

    def _detect_database(self, deps: dict) -> str:
        if "prisma" in deps or "@prisma/client" in deps:
            return "Prisma (DB varies)"
        if "pg" in deps:
            return "PostgreSQL"
        if "mysql2" in deps:
            return "MySQL"
        if "mongoose" in deps or "mongodb" in deps:
            return "MongoDB"
        if "better-sqlite3" in deps or "sqlite3" in deps:
            return "SQLite"
        if "drizzle-orm" in deps:
            return "Drizzle ORM"
        if "typeorm" in deps:
            return "TypeORM"
        return ""

    def _detect_services(self, deps: dict) -> list[str]:
        services = []
        markers = {
            "redis": "Redis", "ioredis": "Redis",
            "@aws-sdk": "AWS", "aws-sdk": "AWS",
            "stripe": "Stripe", "@sentry/node": "Sentry",
            "openai": "OpenAI", "@anthropic-ai/sdk": "Anthropic Claude",
        }
        for marker, name in markers.items():
            if any(marker in d for d in deps):
                if name not in services:
                    services.append(name)
        return services

    def _find_entry_points(self, pkg_data: dict) -> list[str]:
        eps = []
        main = pkg_data.get("main")
        if main:
            eps.append(main)

        for f in ["index.js", "index.ts", "app.js", "app.ts", "server.js", "server.ts"]:
            if (self.root / f).exists() or (self.root / "src" / f).exists():
                eps.append(f)
                break
        return eps

    def _detect_env_vars(self) -> list[str]:
        env_vars = set()
        for env_file in [".env.example", ".env.sample", ".env.local.example"]:
            path = self.root / env_file
            if path.exists():
                for line in read_file_safe(path).splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        env_vars.add(line.split("=", 1)[0].strip())
        return sorted(env_vars)
