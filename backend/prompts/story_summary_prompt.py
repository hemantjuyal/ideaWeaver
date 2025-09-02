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