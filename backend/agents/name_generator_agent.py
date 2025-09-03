from crewai import Agent, Task, Crew, Process
from langsmith import traceable
from backend.agents.character_name_generator import generate_character_names # Import the original function

@traceable(name="Character Name Generator Agent (CrewAI)")
def name_generator_agent(llm):
    """Defines the CrewAI Agent for generating character names."""
    return Agent(
        role='Creative Character Namer',
        goal='Generate distinct and fitting character names based on story premise, age group, and number of characters.',
        backstory='You are an expert at crafting memorable and evocative names for fictional characters that fit the genre and tone of a story.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

@traceable(name="Generate Character Names Task")
def generate_character_names_task(llm, premise: str, age_group: str, num_characters: int):
    """Defines the CrewAI Task for generating character names."""
    agent = name_generator_agent(llm)
    task = Task(
        description=(
            f"Generate {num_characters} distinct and fitting character names for a story with the premise: '{premise}'. "
            f"Target audience: {age_group}. "
            "The output should be a Python list of strings, e.g., ['Name1', 'Name2']."
        ),
        agent=agent,
        expected_output=f"A Python list of {num_characters} strings, where each string is a unique character name. Example: ['Elara', 'Kaelen']"
    )
    return task

# Note: The actual execution of generate_character_names will happen within the CrewAI process
# when this task is run. The agent's response will be the list of names.
