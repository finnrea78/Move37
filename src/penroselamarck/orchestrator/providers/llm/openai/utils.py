"""OpenAI provider helper functions."""

from __future__ import annotations

import re


def normalize_value_key(raw: str) -> str:
    """Normalize arbitrary value text into a stable key slug."""
    value = raw.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:128]
