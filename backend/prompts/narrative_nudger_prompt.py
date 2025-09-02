NARRATIVE_NUDGER_PROMPT = """Introduce an unexpected narrative twist to the following story.

**Current Story Setup**:
---
{world_and_characters}
---

**Target Audience**: {age_group}

The twist should be surprising but logically consistent with the established world and characters.

**Output Format**: Your output MUST use the following Markdown heading:

## Narrative Twist

[Describe the twist here]"""