CHARACTER_CREATOR_PROMPT = """Create compelling characters for the following story world.

**Story World Details**:
---
{world_details}
---

**Character Names to Use (STRICTLY USE THESE NAMES, DO NOT GENERATE NEW ONES)**: {initial_character_names}
**Target Audience**: {age_group}

For each character, describe their role in the story, their personality, their motivations, and their potential story arc.

**Output Format**: Your output MUST use the following Markdown structure for EACH character. Do not include any other text or conversational filler.

## [Character Name]

- **Role in Story**: [Their role, e.g., The Chosen One, The Mentor]
- **Personality Traits**: [e.g., Brave, curious, cynical]
- **Motivation/Goal**: [e.g., To find a lost artifact, to avenge their family]
- **Character Arc**: [e.g., Learns to trust others, overcomes a deep-seated fear]

**Description**:
[A descriptive paragraph that weaves the above details together into a compelling character sketch.]

(Repeat the above structure for each additional character.)

**Example Output (for 2 characters)**:
```markdown
## Elara

- **Role in Story**: The Prophesied Hero
- **Personality Traits**: Brave, compassionate, determined
- **Motivation/Goal**: To unite the fractured kingdoms and defeat the encroaching shadow.
- **Character Arc**: Relearns to trust her inner strength and lead others.

**Description**:
Elara, a young woman with an uncanny connection to ancient magic, carries the weight of a prophecy on her shoulders. Her compassionate nature often puts her at odds with the harsh realities of her world, but her unwavering determination drives her forward.

## Kaelen

- **Role in Story**: The Skeptical Mentor
- **Personality Traits**: Cynical, wise, secretly caring
- **Motivation/Goal**: To protect Elara and atone for past past failures.
- **Character Arc**: Relearns to hope and believe in the possibility of change.

**Description**:
Kaelen, a grizzled veteran of countless battles, has seen too much to believe in prophecies. His cynical exterior hides a deep-seated care for those he protects, especially Elara. He reluctantly guides her, hoping to prevent her from making the same mistakes he once did.
```
"""