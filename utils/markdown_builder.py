# utils/markdown_builder.py
# This module builds the final markdown content for the story summary.

def build_markdown(
    title: str,
    premise: str,
    age_group: str,
    summary: str,
    world_details: str,
    character_details: str,
    narrative_twist: str
) -> str:
    """Builds the final markdown output from all generated story components.

    Args:
        title (str): The title of the story.
        premise (str): The initial premise of the story.
        age_group (str): The target age group for the story.
        summary (str): The generated story summary.
        world_details (str): Detailed description of the story's world.
        character_details (str): Detailed descriptions of the characters.
        narrative_twist (str): The narrative twist or challenge.

    Returns:
        str: The complete story content formatted in Markdown.
    """

    # The character_details are now expected to be a pre-formatted Markdown string.
    # No JSON parsing is needed.

    return f"""# {title}

> **Premise**: {premise}
> **Target Audience**: {age_group}

---

## 📖 Story Summary

{summary}

---

{world_details}

---

## 👥 Characters

{character_details}

---

{narrative_twist}
"""