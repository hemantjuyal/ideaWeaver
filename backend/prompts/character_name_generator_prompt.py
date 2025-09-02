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