"""
Prompt loading and assembly for Gemini metadata extraction (v2).

Loads prompt.md template and fills in the taxonomy from config.py.
All categorical fields and 0-100 scoring scales are documented
inline in prompt.md with explanations for each value.
"""

from pathlib import Path

from config import (
    PROMPT_FILE,
    TAXONOMY,
)


def _format_taxonomy() -> str:
    """Format the domain/sub-domain taxonomy for the prompt."""
    lines = []
    for domain, subdomains in TAXONOMY.items():
        lines.append(f"**{domain}**")
        for sd in subdomains:
            lines.append(f"  - `{sd}`")
        lines.append("")  # blank line between domains
    return "\n".join(lines)


def load_system_prompt() -> str:
    """
    Load the system prompt from prompt.md and fill in the taxonomy.
    
    Only {taxonomy} is injected from config.py. Other categorical fields
    are documented inline in prompt.md with full explanations.
    """
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE}")
    
    template = PROMPT_FILE.read_text(encoding="utf-8")
    
    # Fill in taxonomy placeholder
    prompt = template.format(taxonomy=_format_taxonomy())
    
    return prompt


def build_user_prompt(conversation_text: str) -> str:
    """Build the user prompt with conversation content."""
    return f'''Analyze this conversation and extract metadata:

---
{conversation_text}
---

Return ONLY the JSON object with extracted metadata. No markdown formatting.'''
