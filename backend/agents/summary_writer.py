# agents/summary_writer.py
# This module defines the Summary Writer agent for the ideaWeaver application.

from crewai import Agent
from langsmith import traceable

@traceable(name="Summary Writer Agent")
def summary_writer(llm):
    """Defines the Summary Writer agent with its role, goal, and backstory."""
    return Agent(
        role="Expert Story Summarizer",
        goal="Given the full story context (world, characters, and narrative twist) from the context, craft a single, engaging paragraph that summarizes the story setup in under 100 words, capturing the essence of the world, characters, and plot twist in a tone appropriate for the target audience.",
        backstory=(
            "As a master of the story blurb, you can distill complex narratives into short, compelling summaries. "
            "You know how to hook a reader, conveying the core conflict and character dynamics while maintaining the story's intended tone and mystery. "
            "You are skilled at analyzing the full story context provided to craft a concise and compelling summary."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
