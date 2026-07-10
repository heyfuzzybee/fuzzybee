"""Security utilities: injection prevention, secret redaction."""
from __future__ import annotations

import html
import re
import unicodedata
from typing import List


class InjectionSanitizer:
    """Sanitize input to prevent injection attacks."""

    MAX_LENGTH = 100_000

    def sanitize(self, text: str) -> str:
        """NFKC normalization, strip zero-width, decode HTML, cap length."""
        text = unicodedata.normalize("NFKC", text)
        # Strip zero-width and control characters
        text = re.sub(r"[\u200b-\u200f\ufeff\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
        text = html.unescape(text)
        if len(text) > self.MAX_LENGTH:
            text = text[:self.MAX_LENGTH]
        return text

    def detect_jailbreak(self, text: str) -> bool:
        """Detect common jailbreak patterns."""
        patterns = [
            r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions",
            r"you\s+are\s+(?:now|not\s+an?\s+AI)",
            r"DAN|do\s+anything\s+now",
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)


class SecretRedactor:
    """Redact secrets from logs and outputs."""

    PATTERNS = [
        (r"sk-proj-[a-zA-Z0-9_-]+", "[REDACTED-OPENAI]"),
        (r"sk-live-[a-zA-Z0-9]+", "[REDACTED-STRIPE]"),
        (r"AKIA[0-9A-Z]{16}", "[REDACTED-AWS]"),
        (r"ghp_[a-zA-Z0-9]{36}", "[REDACTED-GITHUB]"),
    ]

    def redact(self, text: str) -> str:
        for pattern, replacement in self.PATTERNS:
            text = re.sub(pattern, replacement, text)
        return text
