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
from backend.utils.llm_loader import load_llm
from backend.utils.save_to_markdown import save_to_markdown
from crewai import Crew, Process, Task, Agent

# --- Pydantic Models for API Contract ---
# This defines the structure of the request body
class UserRequest(BaseModel):
    conversation_history: str
    user_input: str
    collected_inputs: Dict[str, Any]

# This defines the structure of the response body
class AgentResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class StoryGenerationRequest(BaseModel):
    initial_premise: str
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
            collected_inputs=request.collected_inputs
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
    logging.info(f"Received request for /generate_story endpoint with premise: {request.initial_premise}")
    try:
        # Initialize agents
        wb_agent = world_builder(llm)
        cc_agent = character_creator(llm)
        nn_agent = narrative_nudger(llm)
        sw_agent = summary_writer(llm)

        # Determine character names (either provided or generated)
        actual_character_names = request.character_names_input
        if request.name_choice == "Generate for me":
            actual_character_names = generate_character_names(llm, request.initial_premise, request.age_group, request.num_characters)

        # --- Define Tasks ---
        # World Building Task
        world_task = Task(
            description=f"Develop a detailed world description for a story with the premise: '{request.initial_premise}'. "
                        f"Target audience: {request.age_group}. Focus on unique elements, settings, and atmosphere.",
            agent=wb_agent,
            expected_output="A detailed, engaging world description for the story."
        )

        # Character Creation Task
        character_task = Task(
            description=f"Create {request.num_characters} character profiles based on the premise: '{request.initial_premise}' "
                        f"and the world description. Use these names: {actual_character_names}. "
                        f"Include archetypes, key traits, and motivations for each.",
            agent=cc_agent,
            expected_output="A list of detailed character profiles, including names, for the story."
        )

        # --- Create Crew and Kickoff ---
        tasks = [world_task, character_task]

        story_crew = Crew(
            agents=[wb_agent, cc_agent, nn_agent, sw_agent], # Removed ng_agent
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )

        # Execute the crew
        crew_result = story_crew.kickoff()

        # Handle title generation separately if chosen
        generated_title = None
        if request.title_choice == "Generate for me":
            generated_title = generate_story_title(llm, request.initial_premise, request.age_group)

        # Prepare the final output
        final_output = {
            "premise": request.initial_premise,
            "age_group": request.age_group,
            "title_choice": request.title_choice,
            "title": request.title_input if request.title_choice == "Provide my own" else generated_title,
            "num_characters": request.num_characters,
            "name_choice": request.name_choice,
            "character_names": actual_character_names,
            "world_description": crew_result.get("world_description", "N/A"),
            "character_profiles": crew_result.get("character_profiles", "N/A"),
            "narrative_twist": crew_result.get("narrative_twist", "N/A"),
            "story_summary": crew_result.get("story_summary", "N/A")
        }
        
        # Save to markdown (optional, as per original app.py)
        save_to_markdown(final_output["title"], json.dumps(final_output, indent=2))

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