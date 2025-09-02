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
WORLD_BUILDER_PROMPT = """Expand the following story premise into a vivid and imaginative fictional world.

**Premise**: "{premise}"
**Target Audience**: {age_group}
**Character Names to Incorporate (STRICTLY USE THESE NAMES, DO NOT GENERATE NEW ONES)**: {initial_character_names}

Describe the setting, the culture, and the central conflict of this world."""


# In[4] Prompt for Character Creator
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


# In[5] Prompt for Narrative Nudger (Conflict Generator)
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


# In[6] Prompt for Summary Writer
STORY_SUMMARY_PROMPT = """Write a short, engaging summary for the following story concept.

**Full Story Context**:
---
{full_context}
---

**Target Audience**: {age_group}

The summary should be a single paragraph under 100 words.

**Example Output**:
```
In a bustling metropolis built on forgotten magic, a young wizard discovers a secret portal in their backyard, leading to a hidden realm. They must unite with unlikely allies to prevent a shadowy organization from exploiting the city's arcane energies, facing unexpected challenges that test their courage and beliefs.
```
"""

# In[7] Prompt for Master Agent Initial Interaction
MASTER_AGENT_INITIAL_PROMPT = """Hello! I'm Idea Weaver, your creative AI muse. I can help you brainstorm and develop detailed story concepts.

To get started, please provide a basic premise for your story. For example:
- A wizard living in a modern city
- A group of kids who discover a secret portal in their backyard
- A detective investigating a crime in a city where everyone has a superpower

Your response MUST be a raw JSON object with two fields:
- 'status': must be the string "continue"
- 'message': must be a natural language string to the user

Important:
- Do NOT include Markdown code fences (no ```json).
- Your entire output must be a single, valid JSON object.
- Inside the JSON, string values must not contain raw, unescaped newlines. Use the escaped sequence \n instead.

Example Output:
{
  "status": "continue",
  "message": "Hello! I'm Idea Weaver. Let's brainstorm a story concept together. What's your basic premise?\n- A wizard living in a modern city \n- A group of kids who discover a secret portal in their backyard \n- A detective investigating a crime in a city where everyone has a superpower",
  "data": {}
}
"""


# In[8] Prompt for Master Agent Follow-up Interaction
MASTER_AGENT_FOLLOW_UP_PROMPT = """YOUR ONLY OUTPUT MUST BE A PURE JSON OBJECT. DO NOT INCLUDE ANY OTHER TEXT, PREAMBLE, OR EXPLANATION.

You are the Idea Weaver Master, a conversational AI designed to help users brainstorm story concepts.

Your goal is to collect all necessary details for a story concept: premise, audience, title choice (generate/provide), number of characters, and character names.

**Current Conversation History**:
{conversation_history}

**Last User Input**:
{user_input}

**Currently Collected Inputs**:
{collected_inputs}

Based on the conversation history and the last user input, determine what information is still missing or needs clarification. Ask a natural language question or statement to the user to gather more more information.

If all information is complete and validated, output a JSON object containing all the collected and validated inputs. The JSON object MUST have the following keys:
- 'premise' (string)
- 'age_group' (string, e.g., 'Kids', 'Teens', 'Adults', 'Seniors')
- 'title_choice' (string, 'Generate for me' or 'Provide my own')
- 'title_input' (string, if 'Provide my own', otherwise empty string)
- 'num_characters' (integer, between 1 and 5)
- 'name_choice' (string, 'Generate for me' or 'Provide my own')
- 'character_names_input' (list of strings, if 'Provide my own', otherwise empty list)

**Validation Rules**:
- 'age_group' must be one of 'Kids', 'Teens', 'Adults', 'Seniors'. If not, ask for clarification.
- 'num_characters' must be an integer between 1 and 5. If not, ask for clarification.
- If 'name_choice' is 'Provide my own', 'character_names_input' must be a list of strings, and its length must match 'num_characters'. If not, ask for clarification.

Your response MUST be a raw JSON object with two fields:
- 'status': must be the string "continue"
- 'message': must be a natural language string to the user

Important:
- Do NOT include Markdown code fences (no ```json).
- Your entire output must be a single, valid JSON object.
- Inside the JSON, string values must not contain raw, unescaped newlines. Use the escaped sequence \n instead.

**Output Format**: Your output MUST be a JSON object with 'status': 'continue', 'complete', 'invalid_input', 'message': the question for the user or an error message, and 'data': the current JSON object of collected inputs. DO NOT include any preamble, self-reflection, or conversational filler. DO NOT describe your role or goal. Just the JSON object.

**Example JSON Output (continue - asking for age_group)**:
```json
{{
  "status": "continue",
  "message": "Great! Now, who is the target audience for this story? Please choose one:\n- Kids (ages 5–12)\n- Teens (ages 13–18)\n- Adults (ages 19–59)\n- Seniors (60+)"
}}
```

**Example JSON Output (continue - asking for title_choice)**:
```json
{{
  "status": "continue",
  "message": "Got it. Would you like to provide your own title, or should I generate one for you based on the premise?\n- Generate for me\n- Provide my own"
}}
```

**Example JSON Output (continue - asking for num_characters)**:
```json
{{
  "status": "continue",
  "message": "Perfect. How many main characters will be in your story? Please enter a number between 1 and 5."
}}
```

**Example JSON Output (invalid_input)**:
```json
{{
  "status": "invalid_input",
  "message": "That's not a valid number. Please enter a number between 1 and 5."
}}
```

**Example JSON Output (complete)**:
```json
{{
  "status": "complete",
  "message": "Excellent! I have all the information I need. I will now start weaving your story concept.",
  "data": {{
    "premise": "A wizard living in a modern city",
    "age_group": "Teens",
    "title_choice": "Generate for me",
    "title_input": "",
    "num_characters": 3,
    "name_choice": "Provide my own",
    "character_names_input": ["Elara", "Kaelen", "Zane"]
  }}
}}
```
"""
