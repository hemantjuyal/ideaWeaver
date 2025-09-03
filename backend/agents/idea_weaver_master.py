import ast
import json
import logging
import re
from typing import Optional
from crewai import Agent, Task, Crew, Process
from langsmith import traceable
# Import the new tool classes directly
from backend.utils.master_agent_tools import (
    AskForPremiseTool,
    ValidateAndUpdatePremiseTool,
    ValidateAndUpdateAgeGroupTool,
    ValidateAndUpdateTitleChoiceTool,
    ValidateAndUpdateTitleInputTool,
    ValidateAndUpdateNumCharactersTool,
    ValidateAndUpdateNameChoiceTool,
    ValidateAndUpdateCharacterNamesInputTool,
    ProvideOptionsTool,
    SignalCompletionTool,
)

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@traceable(name="Idea Weaver Master Agent")
def idea_weaver_master(llm):
    """Defines the Idea Weaver Master agent with its role, goal, and backstory."""
    return Agent(
        role="Conversational Story Concept Orchestrator",
        goal="Engage the user in a natural conversation to gather all necessary details "
        "(premise, audience, title choice, number of characters, and character names) for a story concept. " \
        "Validate inputs and ensure all information is complete before signaling readiness for story generation.",
        backstory=(
            "You are the primary interface between the user and the Idea Weaver application. "
            "Your expertise lies in understanding user intent, asking clarifying questions, "
            "and ensuring all required story parameters are collected accurately and efficiently. "
            "You are patient, adaptable, and focused on guiding the user through the input process seamlessly."
            "You will manage the entire input collection process, including handling choices for generating or providing titles/names, and managing sequential input for character names."
            "Once all inputs are collected, you will output a JSON object containing all the validated inputs."
        ),
        verbose=True,  # Set to False to prevent detailed execution logs from appearing in UI
        allow_delegation=False,
        llm=llm,
                tools=[
            AskForPremiseTool(),
            ValidateAndUpdatePremiseTool(),
            ValidateAndUpdateAgeGroupTool(),
            ValidateAndUpdateTitleChoiceTool(),
            ValidateAndUpdateTitleInputTool(),
            ValidateAndUpdateNumCharactersTool(),
            ValidateAndUpdateNameChoiceTool(),
            ValidateAndUpdateCharacterNamesInputTool(),
            SignalCompletionTool(),
            ProvideOptionsTool(),
        ]
    )


@traceable(name="Master Agent Input Collection Task")
def master_agent_input_task(llm, current_conversation_history: str, current_user_input: str, collected_inputs: dict, last_question: Optional[str] = None):
    """Defines the task for the Master Agent to collect and validate inputs."""
    master_agent = idea_weaver_master(llm)
    
    # Convert collected_inputs dict to a JSON string for the prompt
    collected_inputs_json_str = json.dumps(collected_inputs, indent=2)

    if not current_conversation_history and not current_user_input:
        # Initial call: Force the LLM to call AskForPremiseTool
        task_description = (
            "Your first task is to use the `Ask for Premise` tool. "
            "The tool will return a JSON object. Your final answer must be ONLY that JSON object, exactly as the tool returned it. "
            "Do not add any explanation, any markdown, or any other text."
        )
    else:
        # Follow-up calls: Use the more general tool-routing prompt
        task_description = (
            f"The user's response is: '{current_user_input}'.\n"
            f"The current collected inputs are: {collected_inputs_json_str}.\n"
            "Based on the user's response, you must use the correct validation tool to process it.\n"
            "When calling the tool, you must use the exact `user_input` and `collected_inputs` provided above.\n"
            "You are only allowed to use the tools provided. Do not invent new tools.\n"
            "The validation tools will also ask the next question in the conversation.\n\n"
            "--- Tool Selection Guide ---\n"
            "0. If a previous tool call returned a status of 'invalid_input', you must use the appropriate validation tool again with the *new* `user_input` to re-validate the input. Do not re-use the old `user_input`.\n"
            "1. If the user asks for help, provides an unclear answer, or says 'generate ideas', use `Provide Options`.\n"
            "2. If `collected_inputs` does not contain 'premise', use `Ask for Premise`.\n"
            "3. If `collected_inputs` contains 'premise' but not 'age_group', use `Validate and Update Premise`.\n"
            "4. If `collected_inputs` contains 'age_group' but not 'title_choice', use `Validate and Update Age Group`.\n"
            "5. If `collected_inputs` contains 'title_choice' but not 'title_input' (and title_choice is 'Provide my own'), use `Validate and Update Title Choice`.\n"
            "6. If `collected_inputs` contains 'title_input' but not 'num_characters', use `Validate and Update Title Input`.\n"
            "7. If `collected_inputs` contains 'num_characters' but not 'name_choice', use `Validate and Update Number of Characters`.\n"
            "8. If `collected_inputs` contains 'name_choice' but not 'character_names_input' (and name_choice is 'Provide my own'), use `Validate and Update Name Choice`.\n"
            "9. If `collected_inputs` contains 'character_names_input', use `Validate and Update Character Names Input`.\n"
            "10. If all required inputs are collected, use `Signal Completion`.\n"
            "--------------------------"
        )

    task = Task(
        description=task_description,
        agent=master_agent,
        expected_output="A single, raw JSON object, which is the direct output of the tool you used. No other text or formatting."
    )


    crew = Crew(
        agents=[master_agent],
        tasks=[task],
        process=Process.sequential,  # Only one task for this crew
        verbose=True  # Set to False to prevent detailed execution logs from appearing in UI
    )
    
    try:
        result = crew.kickoff()
        logging.info(f"Master agent raw response: {result.raw}")

        # The JSON parsing logic remains the same as it handles the output format
        # that the UI expects. The LLM will now generate this JSON after tool calls.
        def escape_unescaped_newlines(s: str) -> str:
            """Escape only raw newlines inside JSON strings."""
            fixed = []
            in_string = False
            prev_char = ''
            for c in s:
                if c == '"' and prev_char != '\\':  # toggle string state on unescaped "
                    in_string = not in_string
                if c == '\n' and in_string:  # raw newline inside a string → escape
                    fixed.append('\\n')
                else:
                    fixed.append(c)
                prev_char = c
            return ''.join(fixed)
        
        processed_raw = result.raw

        # Rule 3: Trim whitespace
        processed_raw = processed_raw.strip()

        parsed_result = None
        try:
            # First, try to parse as-is
            parsed_result = json.loads(processed_raw)
        except json.JSONDecodeError as e:
            logging.warning(f"Initial JSON decode failed: {e}. Attempting to fix and retry.")
            # If it fails, try to fix common LLM-induced errors
            
            # Rule 1: Strip Markdown code fences
            json_match = re.search(r'```json\s*(.*?)\s*```', processed_raw, re.DOTALL)
            if json_match:
                processed_raw = json_match.group(1).strip()

            # Rule 2: Escape raw newlines inside strings
            processed_raw = escape_unescaped_newlines(processed_raw)

            # Rule 3: Fix double curly braces {{ ... }} → { ... }
            if processed_raw.startswith("{{") and processed_raw.endswith("}}"):
                processed_raw = processed_raw[1:-1].strip()

            try:
                # Second attempt: try json.loads again after basic cleaning
                parsed_result = json.loads(processed_raw)
                logging.info("Successfully parsed JSON after basic cleaning.")
            except json.JSONDecodeError:
                # Third attempt: try ast.literal_eval for Python dict syntax (e.g., single quotes)
                try:
                    parsed_result = ast.literal_eval(processed_raw)
                    logging.info("Successfully parsed JSON using ast.literal_eval.")
                except (ValueError, SyntaxError) as ast_e:
                    logging.warning(f"JSON decode failed even after all cleaning attempts: {ast_e}. Returning error.")
                    return json.dumps({
                        "status": "error",
                        "message": "The AI returned an unreadable response. Please try again."
                    })

        # After successful parsing (either direct or after cleaning)
        # Basic validation of the parsed result structure
        if parsed_result and "status" in parsed_result and "message" in parsed_result:
            return json.dumps(parsed_result)  # Return as JSON string
        else:
            logging.warning(f"Master agent returned invalid JSON structure: {result.raw}")
            return json.dumps({
                "status": "error",
                "message": "Master agent returned an unexpected response format."
            })
    except Exception as e:
        logging.error(f"Error during master agent kickoff: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": "An internal error occurred while processing your request. Please try again or restart the conversation."
        })
