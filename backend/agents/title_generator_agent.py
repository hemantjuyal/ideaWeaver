from crewai import Agent, Task, Crew, Process
from langsmith import traceable
from backend.agents.title_generator import generate_story_title # Import the original function

@traceable(name="Title Generator Agent (CrewAI)")
def title_generator_agent(llm):
    """Defines the CrewAI Agent for generating story titles."""
    return Agent(
        role='Creative Title Generator',
        goal='Generate a creative, fitting, and age-appropriate title for a story based on its premise and age group.',
        backstory='You are a master of crafting catchy, imaginative, and relevant titles for creative works, ensuring they resonate with the intended audience.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

@traceable(name="Generate Story Title Task")
def generate_story_title_task(llm, story_premise: str, age_group: str):
    """Defines the CrewAI Task for generating a story title."""
    agent = title_generator_agent(llm)
    task = Task(
        description=(
            f"Generate a creative story title for a story with the premise: '{story_premise}'. "
            f"Target audience: {age_group}. "
            "The output should be a short, catchy, and relevant story title (max 8 words)."
        ),
        agent=agent,
        expected_output="A short, catchy, and relevant story title (max 8 words)."
    )
    return task
