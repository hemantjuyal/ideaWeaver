# agents/title_generator.py
# This module generates a creative title for a story using a CrewAI agent.

from crewai import Agent, Task, Crew, Process
from langsmith import traceable
from backend.prompts.title_generator_prompt import TITLE_GENERATOR_PROMPT

@traceable(name="Title Generator Agent")
def generate_story_title(llm, story_premise: str, age_group: str) -> str:
    """Generates a creative story title based on the premise and age group.

    Args:
        llm: The language model to use.
        story_premise (str): The basic premise of the story.
        age_group (str): The target age group for the story.

    Returns:
        str: The generated story title.
    """
    title_agent = Agent(
        role='Creative Title Generator',
        goal='Generate a creative, fitting, and age-appropriate title for a story based on its premise.',
        backstory='You are a master of crafting catchy, imaginative, and relevant titles for creative works, ensuring they resonate with the intended audience.',
        verbose=False,
        allow_delegation=False,
        llm=llm
    )
    task = Task(
        description=TITLE_GENERATOR_PROMPT.format(
            story_premise=story_premise,
            age_group=age_group
        ),
        agent=title_agent,
        expected_output="A short, catchy, and relevant story title (max 8 words)."
    )

    crew = Crew(agents=[title_agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()
    if result:
        return str(result)
    return "A Story Yet to be Titled"
