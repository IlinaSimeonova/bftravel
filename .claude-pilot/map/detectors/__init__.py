"""Framework detection dispatcher."""

import sys
from pathlib import Path

# Ensure .claude-pilot is on sys.path for absolute imports
_pkg_root = str(Path(__file__).resolve().parent.parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from map.detectors.base import DetectorResult
from map.detectors.python_django import DjangoDetector
from map.detectors.python_generic import PythonGenericDetector
from map.detectors.node import NodeDetector
from map.detectors.generic import GenericDetector


# Ordered by specificity — first match wins
_DETECTORS = [
    DjangoDetector,
    PythonGenericDetector,
    NodeDetector,
    GenericDetector,  # always matches
]


def detect_framework(root: Path) -> DetectorResult:
    """Run detectors in priority order, return first match."""
    for detector_cls in _DETECTORS:
        detector = detector_cls(root)
        if detector.detect():
            return detector.analyze()
    # GenericDetector always matches, so we should never get here
    return GenericDetector(root).analyze()
