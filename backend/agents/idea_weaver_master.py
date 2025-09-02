# agents/idea_weaver_master.py
# This module defines the Idea Weaver Master agent for managing conversational flow.

import json
import logging
import re
from crewai import Agent, Task, Crew, Process
from langsmith import traceable
from backend.prompts.master_agent_initial_prompt import MASTER_AGENT_INITIAL_PROMPT
from backend.prompts.master_agent_follow_up_prompt import MASTER_AGENT_FOLLOW_UP_PROMPT

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
        verbose=True, # Set to False to prevent detailed execution logs from appearing in UI
        allow_delegation=False,
        llm=llm
    )

@traceable(name="Master Agent Input Collection Task")
def master_agent_input_task(llm, current_conversation_history: str, current_user_input: str, collected_inputs: dict):
    """Defines the task for the Master Agent to collect and validate inputs."""
    master_agent = idea_weaver_master(llm)
    
    # Convert collected_inputs dict to a JSON string for the prompt
    collected_inputs_json_str = json.dumps(collected_inputs, indent=2)

    if not current_conversation_history and not current_user_input:
        # Initial call, use the initial prompt
        task_description = MASTER_AGENT_INITIAL_PROMPT
    else:
        # Follow-up call, use the follow-up prompt
        task_description = MASTER_AGENT_FOLLOW_UP_PROMPT.format(
            conversation_history=current_conversation_history,
            user_input=current_user_input,
            collected_inputs=collected_inputs_json_str
        )

    task = Task(
        description=task_description,
        agent=master_agent,
                expected_output="""Your response MUST be a pure JSON object, 
                with no additional text or markdown formatting. 
                The JSON object must have 'status' (string: 'continue', 'complete', 'invalid_input') and 
                'message' (string: the question for the user or an error message). 
                It can optionally have 'data' (JSON object with collected inputs if status is 'complete')."""
    )

    crew = Crew(
        agents=[master_agent],
        tasks=[task],
        process=Process.sequential, # Only one task for this crew
        verbose=True # Set to False to prevent detailed execution logs from appearing in UI
    )
    
    try:
        result = crew.kickoff()
        logging.info(f"Master agent raw response: {result.raw}")
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
            # Rule 4: Retry parsing (first attempt)
            parsed_result = json.loads(processed_raw)
        except json.JSONDecodeError as e:
            logging.warning(f"Initial JSON decode failed: {e}. Attempting to fix.")

            # Rule 1: Strip Markdown code fences
            json_match = re.search(r'```json\s*(.*?)\s*```', processed_raw, re.DOTALL)
            if json_match:
                processed_raw = json_match.group(1).strip() # Trim whitespace from extracted JSON
                logging.info(f"Extracted JSON from markdown: {processed_raw}")

            # Rule 2: Escape raw newlines inside strings
            # This regex applies globally, assuming newlines outside strings are structural and would break initial parse
            # The user's example implies this global application is desired for their specific newline issue
            # processed_raw = re.sub(r'(?<!\\)\\n', r'\\\\n', processed_raw)
            processed_raw = escape_unescaped_newlines(processed_raw)

            try:
                # Rule 4: Retry parsing (after cleaning)
                parsed_result = json.loads(processed_raw)
                logging.info("Successfully parsed JSON after cleaning.")
            except json.JSONDecodeError as e_fixed:
                logging.warning(f"JSON decode failed even after cleaning: {e_fixed}. Returning error.")
                # If fixing newlines didn't work, return error
                return json.dumps({"status": "error", "message": "The AI returned an unreadable response. Please try again."})

        # After successful parsing (either direct or after cleaning)
        # Basic validation of the parsed result structure
        if parsed_result and "status" in parsed_result and "message" in parsed_result:
            return json.dumps(parsed_result) # Return as JSON string
        else:
            logging.warning(f"Master agent returned invalid JSON structure: {result.raw}")
            return json.dumps({"status": "error", "message": "Master agent returned an unexpected response format."})
    except Exception as e:
        logging.error(f"Error during master agent kickoff: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": "An internal error occurred while processing your request. Please try again or restart the conversation."})
