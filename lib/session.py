"""Session detection: spawned, headless, interactive."""
from __future__ import annotations

import os
import sys
from enum import Enum
from typing import Optional


class SessionKind(Enum):
    SPAWNED = "spawned"
    HEADLESS = "headless"
    INTERACTIVE = "interactive"


class SessionDetector:
    """Detect session kind for telemetry and gating."""

    def detect(self) -> SessionKind:
        """Determine session kind from environment signals."""
        # CI / headless detection
        ci_vars = [
            "CI", "GITHUB_ACTIONS", "GITLAB_CI", "CIRCLECI", "TRAVIS",
            "JENKINS_URL", "BUILDKITE", "DRONE", "SEMAPHORE",
        ]
        if any(os.environ.get(v) for v in ci_vars):
            return SessionKind.HEADLESS

        # Spawned (child process, no TTY)
        if not sys.stdin.isatty():
            return SessionKind.SPAWNED

        # Default: interactive
        return SessionKind.INTERACTIVE

    def detect_str(self) -> str:
        return self.detect().value
