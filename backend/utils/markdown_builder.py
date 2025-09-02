# utils/markdown_builder.py
# This module builds the final markdown content for the story summary.

import re

def _clean_llm_output(text: str) -> str:
    """Removes any text before the first Markdown heading in a string and specific unwanted headings."""
    # Remove specific unwanted headings first
    text = re.sub(r'^## Narrative Twist\s*\n', '', text, flags=re.MULTILINE)

    # Then remove any text before the first Markdown heading
    match = re.search(r'^#+\s', text, re.MULTILINE)
    if match:
        return text[match.start():]
    return text

def build_markdown(
    title: str,
    premise: str,
    age_group: str,
    initial_character_names: list,
    crew_result
) -> str:
    """Builds the final markdown output from all generated story components."""

    world_details = _clean_llm_output(crew_result.tasks_output[0].raw)
    character_details = _clean_llm_output(crew_result.tasks_output[1].raw)
    narrative_twist_content = _clean_llm_output(crew_result.tasks_output[2].raw)
    summary = crew_result.tasks_output[3].raw

    return f"""# {title}

> **Premise**: {premise}
> **Target Audience**: {age_group}
> **Characters**: {', '.join(initial_character_names)}

---

## Story Summary

{summary}

---

{world_details}

---

## Characters

{character_details}

---

## Narrative Twist

{narrative_twist_content}
"""
