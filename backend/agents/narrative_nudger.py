# agents/narrative_nudger.py
# This module defines the Narrative Nudger agent for the ideaWeaver application.

from crewai import Agent
from langsmith import traceable

@traceable(name="Narrative Nudger Agent")
def narrative_nudger(llm):
    """Defines the Narrative Nudger agent with its role, goal, and backstory."""
    return Agent(
        role="Master of Narrative Tension",
        goal="Given the world and character details from the context, introduce a single, unexpected, yet fitting narrative twist that adds depth, tension, or surprise to the story, ensuring it is aligned with the established world and characters.",
        backstory=(
            "As a seasoned storyteller, you excel at creating moments of conflict and intrigue. "
            "Your talent lies in seeing the narrative threads and weaving in a twist that feels both shocking and inevitable. "
            "You are adept at extracting the world and character details from the provided context to craft a relevant twist."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
