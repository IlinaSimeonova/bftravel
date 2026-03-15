"""Base detector interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppInfo:
    """Info about a single app/module in the project."""
    name: str
    path: str
    purpose: str = ""
    model_count: int = 0
    view_count: int = 0
    form_count: int = 0
    template_count: int = 0
    has_admin: bool = False
    has_tasks: bool = False
    has_tests: bool = False
    management_commands: list[str] = field(default_factory=list)
    key_files: list[str] = field(default_factory=list)


@dataclass
class DetectorResult:
    """Result of framework detection and analysis."""
    framework: str = "Unknown"
    framework_version: str = ""
    language: str = "Unknown"
    language_version: str = ""
    database: str = ""
    port: str = ""
    services: list[str] = field(default_factory=list)
    apps: list[AppInfo] = field(default_factory=list)
    config_dir: str = ""
    template_dir: str = ""
    static_dir: str = ""
    entry_points: list[str] = field(default_factory=list)
    middleware: list[str] = field(default_factory=list)
    installed_apps: list[str] = field(default_factory=list)
    env_vars: list[str] = field(default_factory=list)
    extra: dict = field(default_factory=dict)


class BaseDetector(ABC):
    """Abstract base for framework detectors."""

    def __init__(self, root: Path):
        self.root = root

    @abstractmethod
    def detect(self) -> bool:
        """Return True if this detector matches the project."""
        ...

    @abstractmethod
    def analyze(self) -> DetectorResult:
        """Perform deep analysis and return structured result."""
        ...
