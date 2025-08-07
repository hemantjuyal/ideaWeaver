# utils/prompt_templates.py
# This module contains the prompt templates used by various agents in the ideaWeaver application.
"""This module defines the prompt templates used by various agents in the Idea Weaver application.

Each template is a multi-line string that can be formatted with specific variables
to guide the behavior of the language models.
"""

# In[1] Prompt for Title Generator
TITLE_GENERATOR_PROMPT = """Based on the story premise and target audience below, generate a short and engaging story title.

Premise: "{story_premise}"
Target Audience: {age_group}

Requirements:
- Title should be no more than 8 words.
- Make it catchy, imaginative, and relevant to the premise.
- Avoid generic phrases or clichés.
- Ensure the tone is appropriate for the target audience."""

# In[2] Prompt for Character Name Generator
CHARACTER_NAME_GENERATOR_PROMPT = """You are a creative naming expert specializing in fictional characters.

**Goal**: Generate {num_characters} distinct and fitting character names based on a story premise and target audience.

**Story Premise**: "{premise}"
**Target Audience**: {age_group}

**Instructions**:
1.  Generate exactly {num_characters} names.
2.  The names should be creative, memorable, and suitable for the premise.
3.  The names must be unique and not variations of each other.

**Output Format**: Your output MUST be a single, valid Python list of {num_characters} strings, with no other text, explanation, or markdown.

**Example Output**:
```python
["Aria Stormrider", "Zane Emberfall"]
```
"""

# In[3] Prompt for Premise Expander (World Builder)
WORLD_BUILDER_PROMPT = """You are a world-building expert for creative fiction.

**Goal**: Expand a basic story premise into a vivid, imaginative, and coherent fictional world, ensuring it is suitable for the target audience and incorporates the provided character names.

**Story Premise**: "{premise}"
**Target Audience**: {age_group}
**Character Names to Incorporate**: {initial_character_names}

**Instructions**:
1.  **Setting**: Describe the setting clearly (place, environment, time period).
2.  **Context**: Provide world context (culture, rules, magic systems, technology).
3.  **Conflict**: Identify the **central conflict or source of tension** that will drive the story.
4.  **Integration**: Naturally integrate the provided character names into the world's description, giving them a clear place or context.

**Output Format**: Your output MUST be structured with the following Markdown headings. Do not include any other text or conversational filler.

# World Details

## Setting Description
<Your vivid description here>

## World Context
<Explanation of world dynamics, tone, or societal backdrop>

## Central Conflict
<Describe the main struggle or issue in this world>
"""


# In[4] Prompt for Character Creator
CHARACTER_CREATOR_PROMPT = """You are a character creation expert for fictional stories.

**Goal**: Create compelling, original characters who naturally belong in the provided story world, using the pre-defined character names.

**Story World Details**:
---
{world_details}
---

**Character Names to Use**: {initial_character_names}
**Target Audience**: {age_group}

**Instructions**:
1.  For each character name provided, create their role, personality, motivation, and potential story arc.
2.  Ensure the characters feel like they truly belong in the story world.
3.  Avoid clichés and ensure characters are well-developed and age-appropriate.

**Output Format**: Your output MUST use the following Markdown structure for EACH character. Do not include any other text or conversational filler.

## [Character Name]

- **Role in Story**: [Their role, e.g., The Chosen One, The Mentor]
- **Personality Traits**: [e.g., Brave, curious, cynical]
- **Motivation/Goal**: [e.g., To find a lost artifact, to avenge their family]
- **Character Arc**: [e.g., Learns to trust others, overcomes a deep-seated fear]

**Description**:
[A descriptive paragraph that weaves the above details together into a compelling character sketch.]

(Repeat the above structure for each additional character.)
"""


# In[5] Prompt for Narrative Nudger (Conflict Generator)
NARRATIVE_NUDGER_PROMPT = """You are a master of narrative tension and plot twists.

**Goal**: Introduce one unexpected yet fitting narrative development to add depth and tension to the story.

**Current Story Setup**:
---
{world_and_characters}
---

**Target Audience**: {age_group}

**Instructions**:
1.  Create a single, compelling narrative twist.
2.  The twist must be unexpected but logically consistent with the established world and characters.
3.  It should raise the emotional stakes or escalate the plot.

**Output Format**: Your output MUST use the following Markdown heading. Do not include any other text or conversational filler.

## Narrative Twist

[Describe the twist in 3-5 vivid and compelling sentences. Be specific about who is involved and how it changes the story.]
"""


# In[6] Prompt for Summary Writer
STORY_SUMMARY_PROMPT = """You are a skilled story summarizer, expert at crafting compelling blurbs.

**Goal**: Write a single, engaging paragraph that summarizes the entire story setup in under 100 words.

**Full Story Context**:
---
{full_context}
---

**Target Audience**: {age_group}

**Instructions**:
1.  Write a single, continuous paragraph.
2.  The summary must be under 100 words.
3.  Clearly convey the world, main characters, and the central twist from the context provided.
4.  Match the tone and vocabulary for the specified age group.
5.  Make it feel like a compelling back-cover blurb that sparks curiosity.

**Output Format**: Your output MUST be a single paragraph of text. Do not include any headings, titles, or conversational filler.
"""