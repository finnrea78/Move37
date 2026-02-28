"""Prompt rendering helpers.

``render_user_prompt`` fills the user prompt template with runtime variables.
Using a dedicated helper centralizes formatting behavior and error reporting.
"""

from __future__ import annotations


def render_user_prompt(template: str, variables: dict[str, str]) -> str:
    """Render one user prompt template with explicit variable substitution.

    Args:
        template: Prompt template text, using ``str.format`` placeholders.
        variables: Mapping of placeholder names to rendered values.

    Returns:
        A fully rendered prompt string.

    Raises:
        ValueError: If required template variables are missing.
    """
    try:
        return template.format(**variables)
    except KeyError as exc:
        missing_key = str(exc).strip("'")
        raise ValueError(f"Missing prompt template variable: {missing_key}") from exc
