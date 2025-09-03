import re
from typing import Dict, Any, List

def _clean_llm_output(text: str) -> str:
    """Removes any text before the first Markdown heading in a string and specific unwanted headings."""
    # Remove specific unwanted headings first
    text = re.sub(r'^## Narrative Twist\s*\n', '', text, flags=re.MULTILINE)

    # Then remove any text before the first Markdown heading
    match = re.search(r'^#+\s', text, re.MULTILINE)
    if match:
        return text[match.start():]
    return text

def build_markdown(final_output: Dict[str, Any]) -> str:
    """Builds the final markdown output from all generated story components."""

    title = final_output.get("title", "Untitled Story")
    premise = final_output.get("premise", "N/A")
    age_group = final_output.get("age_group", "N/A")
    character_names = final_output.get("character_names", [])
    world_description = _clean_llm_output(final_output.get("world_description", "N/A"))
    character_profiles = _clean_llm_output(final_output.get("character_profiles", "N/A")),
    narrative_twist_content = _clean_llm_output(final_output.get("narrative_twist", "N/A"))
    summary = final_output.get("story_summary", "N/A")

    return f"""# {title}

> **Premise**: {premise}
> **Target Audience**: {age_group}
> **Characters**: {', '.join(character_names)}

---

## Story Summary

{summary}

---

{world_description}

---

## Characters

{character_profiles}

---

## Narrative Twist

{narrative_twist_content}
"""