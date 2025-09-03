import json
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

# your agent and task functions are in this path
from backend.agents.idea_weaver_master import master_agent_input_task
from backend.agents.world_builder import world_builder
from backend.agents.character_creator import character_creator
from backend.agents.narrative_nudger import narrative_nudger
from backend.agents.summary_writer import summary_writer
from backend.agents.title_generator import generate_story_title
from backend.agents.character_name_generator import generate_character_names
from backend.agents.name_generator_agent import name_generator_agent, generate_character_names_task
from backend.agents.title_generator_agent import title_generator_agent, generate_story_title_task
from backend.utils.llm_loader import load_llm
from backend.utils.save_to_markdown import save_to_markdown
from crewai import Crew, Process, Task, Agent

# --- Pydantic Models for API Contract ---
# This defines the structure of the request body
class UserRequest(BaseModel):
    conversation_history: str
    user_input: str
    collected_inputs: Dict[str, Any]
    last_question: Optional[str] = None

# This defines the structure of the response body
class AgentResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class StoryGenerationRequest(BaseModel):
    premise: str
    age_group: str
    title_choice: str
    title_input: Optional[str] = None
    num_characters: int
    name_choice: str
    character_names_input: Optional[list[str]] = None


router = APIRouter()
llm = load_llm() # Load your LLM once on startup

@router.post("/converse", response_model=AgentResponse)
async def converse(request: UserRequest):
    logging.info(f"Received request for /converse endpoint with input: {request.user_input}")
    logging.info(f"Collected inputs received by backend: type={type(request.collected_inputs)}, content={request.collected_inputs}")
    try:
        # Call your existing agent task function
        agent_json_string = master_agent_input_task(
            llm=llm,
            current_conversation_history=request.conversation_history,
            current_user_input=request.user_input,
            collected_inputs=request.collected_inputs,
            last_question=request.last_question
        )
        
        # The function already returns a JSON string, so we parse it back to a dict
        # FastAPI will then re-serialize it into a proper HTTP response.
        agent_response_dict = json.loads(agent_json_string)

        # Validate that the response from the agent contains the required fields
        if "status" not in agent_response_dict or "message" not in agent_response_dict:
            return AgentResponse(status="error", message="Internal agent returned invalid format.")

        logging.info("Successfully processed /converse request.")
        return agent_response_dict

    except json.JSONDecodeError:
        # This catches errors if the agent returns a non-JSON string
        return AgentResponse(status="error", message="Internal agent response was not valid JSON.")
    except Exception as e:
        # This catches any other unexpected errors
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        return AgentResponse(status="error", message="An unexpected error occurred on the server.")

@router.post("/generate_story")
async def generate_story(request: StoryGenerationRequest):
    logging.info(f"Received request for /generate_story endpoint with premise: {request.premise}")
    try:
        # Initialize agents
        wb_agent = world_builder(llm)
        cc_agent = character_creator(llm)
        nn_agent = narrative_nudger(llm)
        sw_agent = summary_writer(llm)
        # Initialize new agents
        ng_agent = name_generator_agent(llm)
        tg_agent = title_generator_agent(llm)

        tasks = []
        agents_in_crew = [wb_agent, cc_agent, nn_agent, sw_agent]

        # Add title generation task if chosen
        generated_title = None
        if request.title_choice == "Generate for me":
            title_task = generate_story_title_task(llm, request.premise, request.age_group)
            tasks.append(title_task)
            agents_in_crew.append(tg_agent)
        else:
            generated_title = request.title_input # Use provided title

        # Add character name generation task if chosen
        actual_character_names = request.character_names_input
        if request.name_choice == "Generate for me":
            names_task = generate_character_names_task(llm, request.premise, request.age_group, request.num_characters)
            tasks.append(names_task)
            agents_in_crew.append(ng_agent)
        # else: actual_character_names is already set from request.character_names_input

        # World Building Task
        world_task = Task(
            description=f"Develop a detailed world description for a story with the premise: '{request.premise}'. "
                        f"Target audience: {request.age_group}. Focus on unique elements, settings, and atmosphere.",
            agent=wb_agent,
            expected_output="A detailed, engaging world description for the story."
        )
        tasks.append(world_task)

        # Character Creation Task
        # This task now depends on names being generated or provided.
        # We'll need to ensure the names are available from the crew_result if generated.
        character_task = Task(
            description=f"Create {request.num_characters} character profiles based on the premise: '{request.premise}' "
                        f"and the world description. Use these names: {{crew_result_names}}. " # Placeholder for names
                        f"Include archetypes, key traits, and motivations for each.",
            agent=cc_agent,
            expected_output="A list of detailed character profiles, including names, for the story."
        )
        tasks.append(character_task)

        # Narrative Nudger Task
        narrative_task = Task(
            description=f"Develop a compelling narrative twist or plot point for the story based on the premise: '{request.premise}', "
                        f"world description: {{crew_result_world_description}}, and character profiles: {{crew_result_character_profiles}}.",
            agent=nn_agent,
            expected_output="A concise and engaging narrative twist or plot point."
        )
        tasks.append(narrative_task)

        # Summary Writer Task
        summary_task = Task(
            description=f"Write a concise and engaging summary of the story, incorporating the premise: '{request.premise}', "
                        f"world description: {{crew_result_world_description}}, character profiles: {{crew_result_character_profiles}}, "
                        f"and narrative twist: {{crew_result_narrative_twist}}.",
            agent=sw_agent,
            expected_output="A short, engaging story summary."
        )
        tasks.append(summary_task)


        # --- Create Crew and Kickoff ---
        # Ensure unique agents in the crew
        story_crew = Crew(
            agents=list(set(agents_in_crew)), # Use set to ensure unique agents
            tasks=tasks,
            process=Process.sequential, # Keep sequential for now, can be changed to hierarchical later
            verbose=False
        )

        # Execute the crew
        story_crew.kickoff()

        # Extract results from crew_result
        # CrewAI returns results as a dictionary where keys are task outputs
        # We need to map these back to our final_output structure
        task_outputs = {}
        for task_output in story_crew.tasks_outputs:
            task_outputs[task_output.description] = task_output.result
        
        # If title was generated by crew, get it from task_outputs
        if request.title_choice == "Generate for me":
            generated_title = task_outputs.get(title_task.description, generated_title) # Use task description as key

        # If names were generated by crew, get them from task_outputs
        if request.name_choice == "Generate for me":
            actual_character_names = task_outputs.get(names_task.description, actual_character_names) # Use task description as key

        # Prepare the final output
        final_output = {
            "premise": request.premise,
            "age_group": request.age_group,
            "title_choice": request.title_choice,
            "title": generated_title, # Now directly from generated_title or request.title_input
            "num_characters": request.num_characters,
            "name_choice": request.name_choice,
            "character_names": actual_character_names, # Now directly from actual_character_names or request.character_names_input
            "world_description": task_outputs.get(world_task.description, "N/A"),
            "character_profiles": task_outputs.get(character_task.description, "N/A"),
            "narrative_twist": task_outputs.get(narrative_task.description, "N/A"),
            "story_summary": task_outputs.get(summary_task.description, "N/A")
        }
        
        # Build markdown content using the new build_markdown function
        from backend.utils.markdown_builder import build_markdown
        markdown_content = build_markdown(final_output)

        # Save to markdown
        save_to_markdown(final_output["title"], markdown_content)

        logging.info("Successfully processed /generate_story request.")
        return {"status": "complete", "message": "Story concept generated successfully!", "data": final_output}

    except Exception as e:
        logging.error(f"Error during story generation: {e}", exc_info=True)
        return {"status": "error", "message": f"An error occurred during story generation: {str(e)}"}

@router.get("/")
def read_root():
    logging.info("Received request for / endpoint.")
    response = {"message": "IdeaWeaver API is running."}
    logging.info("Successfully processed / request.")
    return response