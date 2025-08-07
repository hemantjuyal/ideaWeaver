# agents/character_name_generator.py
# This module generates character names using a dedicated CrewAI agent.

from crewai import Agent, Task, Crew, Process
from utils.prompt_templates import CHARACTER_NAME_GENERATOR_PROMPT
from langsmith import traceable

@traceable(name="Character Name Generator Agent")
def generate_character_names(llm, premise, age_group, num_characters):
    """Generates a specified number of character names using a dedicated agent.

    Args:
        llm: The language model to use.
        premise (str): The story premise.
        age_group (str): The target age group for the story.
        num_characters (int): The number of characters to generate names for.

    Returns:
        list[str]: A list of generated character names.
    """
    character_namer_agent = Agent(
        role='Creative Character Namer',
        goal=f'Generate {num_characters} distinct and fitting character names based on a story premise.',
        backstory='You are an expert at crafting memorable and evocative names for fictional characters that fit the genre and tone of a story.',
        verbose=False,
        allow_delegation=False,
        llm=llm
    )

    task = Task(
        description=CHARACTER_NAME_GENERATOR_PROMPT.format(
            premise=premise,
            age_group=age_group,
            num_characters=num_characters
        ),
        agent=character_namer_agent,
        expected_output=f"A Python list of {num_characters} strings, where each string is a unique character name. Example: ['Elara', 'Kaelen']"
    )

    crew = Crew(
        agents=[character_namer_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    # Kick off the crew and get the raw output
    result = crew.kickoff()
    raw_result = result.raw

    # Process the result to return a clean list of names
    try:
        # The output should be a string representation of a list, e.g., "['Elara', 'Kaelen']"
        # We can use eval to safely parse it into a Python list.
        name_list = eval(raw_result)
        if isinstance(name_list, list) and len(name_list) == num_characters and all(isinstance(n, str) for n in name_list):
            return name_list
    except (SyntaxError, ValueError, TypeError):
        # Fallback in case the output is not a valid list string
        # We can try to split by common delimiters
        cleaned_result = raw_result.strip("[]'\n ").replace("'", "").replace('"', '')
        name_list = [name.strip() for name in cleaned_result.split(',')]
        if len(name_list) >= num_characters:
            return name_list[:num_characters]

    # If all else fails, return a default list of generic names
    return [f"Character {i+1}" for i in range(num_characters)]
