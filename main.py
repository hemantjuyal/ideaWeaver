# main.py
# This is the main entry point for the Idea Weaver application.

from crewai import Task, Crew
from agents.world_builder import world_builder
from agents.character_creator import character_creator
from agents.narrative_nudger import narrative_nudger
from agents.summary_writer import summary_writer
from utils.save_to_markdown import save_to_markdown
from langsmith import traceable

from utils.prompt_templates import (
    WORLD_BUILDER_PROMPT,
    CHARACTER_CREATOR_PROMPT,
    NARRATIVE_NUDGER_PROMPT,
    STORY_SUMMARY_PROMPT,
)
from utils.startup_checker import run_startup_checks
from utils.llm_loader import load_llm
from utils.markdown_builder import build_markdown
from agents.title_generator import generate_story_title
from agents.character_name_generator import generate_character_names


# === Startup Checks ===
run_startup_checks()

# === Load LLM ===
llm = load_llm()

# === Main Run Function ===
@traceable(name="Run Idea Weaver", run_type="chain", tags=["idea-weaver"])
def run_idea_weaver():
    """Runs the Idea Weaver application, guiding the user through story concept generation."""
    print("\nWelcome to Idea Weaver!")
    print("Let's build a story concept together. Just give me a starting point.")

    # === Collect Story Premise ===
    print("\nFirst, enter your basic story premise.")
    print("Examples:")
    print("- A wizard living in a modern city")
    print("- A group of kids who discover a secret portal in their backyard")
    print("- A detective investigating a crime in a city where everyone has a superpower")
    initial_premise = input("\n> Your premise: ")

    # === Choose Target Audience ===
    print("\nTarget Audience: Choose your target age group for the story:")
    print("1. Kids (ages 5–12)")
    print("2. Teens (ages 13–18)")
    print("3. Adults (ages 19–59)")
    print("4. Seniors (60+)")
    age_groups = {
        "1": "Kids",
        "2": "Teens",
        "3": "Adults",
        "4": "Seniors"
    }
    while True:
        age_input = input("> Enter the number corresponding to your target audience (1–4): ").strip()
        if age_input in age_groups:
            age_group = age_groups[age_input]
            break
        else:
            print("Invalid input. Please enter a number between 1 and 4.")

    # === Prompt for Title ===
    print("\nTitle Option: Choose a title option:")
    print("1. Let the app generate a title for you")
    print("2. Enter your own title")
    while True:
        title_choice = input("> Enter your choice (1-2): ").strip()
        if title_choice == "1":
            print("\nGenerating title...")
            title = generate_story_title(llm, initial_premise, age_group)
            print(f'\nGenerated Title: "{title}"')
            break
        elif title_choice == "2":
            print("\nExamples:")
            print("- The Last Spellbinder")
            print("- The Gateway in the Garden")
            print("- City of Heroes")
            title = input("\n> Enter your title: ").strip()
            break
        else:
            print("Invalid input. Please enter 1 or 2.")

    # === Choose Number of Characters ===
    print("\nNumber of Characters: How many characters would you like in your story? (1-5)")
    while True:
        try:
            num_characters = int(input("Enter the number of characters: ").strip())
            if 1 <= num_characters <= 5:
                break
            else:
                print("Invalid input. Please enter a number between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    # === Prompt for Character Names ===
    print("\nCharacter Name Option: Choose a character name option:")
    print("1. Let the app generate character names for you")
    print("2. Enter your own character names")
    while True:
        name_choice = input("Enter your choice (1-2): ").strip()
        if name_choice == "1":
            print("Generating character names...")
            initial_character_names = generate_character_names(llm, initial_premise, age_group, num_characters)
            print(f"Generated Names: {", ".join(initial_character_names)}")
            break
        elif name_choice == "2":
            print(f" You can personalize {num_characters} characters.")
            print("Examples:")
            for i in range(num_characters):
                print(f"- Character {i+1}: [e.g., Name{i+1}]")
            initial_character_names = []
            for i in range(num_characters):
                name = input(f"Enter the name for Character {i+1}: ").strip()
                initial_character_names.append(name)
            print(f" Got it! Using characters: {', '.join(initial_character_names)}")
            break
        else:
            print("Invalid input. Please enter 1 or 2.")

    # === Agent Definitions ===
    world_agent = world_builder(llm)
    character_agent = character_creator(llm)
    narrative_agent = narrative_nudger(llm)
    summary_agent = summary_writer(llm)

    # === Task Definitions ===
    world_task = Task(
        description=WORLD_BUILDER_PROMPT.format(
            premise=initial_premise, 
            age_group=age_group, 
            initial_character_names=initial_character_names
        ),
        agent=world_agent,
        expected_output="A detailed description of the story's world, including setting, context, and conflict."
    )

    character_task = Task(
        description=CHARACTER_CREATOR_PROMPT,
        agent=character_agent,
        expected_output=f"A human-readable description of {num_characters} detailed characters, including name, role, personality, motivation, and arc.",
        context=[world_task]
    )

    narrative_task = Task(
        description=NARRATIVE_NUDGER_PROMPT,
        agent=narrative_agent,
        expected_output="A compelling narrative twist or challenge that adds depth and tension to the story.",
        context=[world_task, character_task]
    )

    summary_task = Task(
        description=STORY_SUMMARY_PROMPT,
        agent=summary_agent,
        expected_output="A concise, single-paragraph summary of the story setup, under 100 words.",
        context=[world_task, character_task, narrative_task]
    )

    # === Crew Execution ===
    story_crew = Crew(
        agents=[world_agent, character_agent, narrative_agent, summary_agent],
        tasks=[world_task, character_task, narrative_task, summary_task],
        verbose=True
    )

    result = story_crew.kickoff()

    # === Build Final Markdown Content ===
    markdown_output = build_markdown(
        title=title,
        premise=initial_premise,
        age_group=age_group,
        summary=result.raw,
        world_details=world_task.output.raw,
        character_details=character_task.output.raw,
        narrative_twist=narrative_task.output.raw
    )

    # === Save to Markdown ===
    save_to_markdown(title, markdown_output)

    return {
        "premise": initial_premise,
        "age_group": age_group,
        "title": title
    }

# === Run the App ===
if __name__ == "__main__":
    run_idea_weaver()