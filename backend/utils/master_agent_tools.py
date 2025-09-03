import json
import re
from typing import Dict, Any, List, Optional, Type
from backend.agents.character_name_generator import generate_character_names
from backend.agents.title_generator import generate_story_title
from backend.utils.llm_loader import load_llm

from crewai.tools import BaseTool # Import BaseTool
from pydantic import BaseModel, Field # Import BaseModel and Field for args_schema


# Load LLM once for tools that need it
_llm_for_tools = load_llm()

class UserInputAndCollectedInputsInput(BaseModel):
    user_input: str = Field(..., description="The user's last input.")
    collected_inputs: Dict[str, Any] = Field(..., description="Current collected inputs dictionary.")

class CollectedInputsInput(BaseModel):
    collected_inputs: Dict[str, Any] = Field(..., description="Current collected inputs dictionary.")

def _parse_user_input(user_input: str) -> str:
    """Helper to clean and normalize user input."""
    return user_input.strip()

def _is_valid_premise(premise: str) -> bool:
    return bool(premise and len(premise) > 10) # Simple validation

def _is_valid_age_group(age_group: str) -> bool:
    return age_group in ["Kids", "Teens", "Adults", "Seniors"]

def _is_valid_title_choice(choice: str) -> bool:
    return choice in ["Generate for me", "Provide my own"]

def _is_valid_num_characters(num: Any) -> bool:
    try:
        n = int(num)
        return 1 <= n <= 5
    except (ValueError, TypeError):
        return False

def _is_valid_name_choice(choice: str) -> bool:
    return choice in ["Generate for me", "Provide my own"]

def _parse_character_names_input(input_str: str, expected_num: int) -> Optional[List[str]]:
    """Attempts to parse a string of names into a list."""
    names = [name.strip() for name in re.split(r'[,;]', input_str) if name.strip()]
    if len(names) == expected_num:
        return names
    return None





# --- Tools for Master Agent (as BaseTool subclasses) ---

class AskForPremiseTool(BaseTool):
    name: str = "Ask for Premise"
    description: str = "Use this tool to initiate the conversation and ask the user for the story premise."

    def _run(self) -> Dict[str, Any]:
        return {
            "status": "continue",
            "message": "Hello! I'm Idea Weaver. Let's brainstorm a story concept together. What's your basic premise?\n- A wizard living in a modern city\n- A group of kids who discover a secret portal in their backyard\n- A detective investigating a crime in a city where everyone has a superpower",
            "data": {},
            "last_question": "premise"
        }


class ValidateAndUpdatePremiseTool(BaseTool):
    name: str = "Validate and Update Premise"
    description: str = "Use this tool to validate the user's input for the story premise and update the collected inputs."
    args_schema: Type[BaseModel] = UserInputAndCollectedInputsInput

    def _run(self, user_input: str, collected_inputs: Dict[str, Any]) -> Dict[str, Any]:
        premise = _parse_user_input(user_input)
        if _is_valid_premise(premise):
            collected_inputs["premise"] = premise
            return {
                "status": "continue",
                "message": "Great! Now, who is the target audience for this story? Please choose one:\n- Kids (ages 5–12)\n- Teens (ages 13–18)\n- Adults (ages 19–59)\n- Seniors (60+)",
                "data": collected_inputs,
                "last_question": "age_group"
            }
        else:
            return {
                "status": "invalid_input",
                "message": "That doesn't seem like a valid premise. Please provide a more detailed story premise (e.g., 'A wizard living in a modern city').",
                "data": collected_inputs,
                "last_question": "premise"
            }


class ValidateAndUpdateAgeGroupTool(BaseTool):
    name: str = "Validate and Update Age Group"
    description: str = "Use this tool to validate the user's input for the target age group and update the collected inputs."
    args_schema: Type[BaseModel] = UserInputAndCollectedInputsInput

    def _run(self, user_input: str, collected_inputs: Dict[str, Any]) -> Dict[str, Any]:
        age_group = _parse_user_input(user_input)
        if _is_valid_age_group(age_group):
            collected_inputs["age_group"] = age_group
            return {
                "status": "continue",
                "message": "Got it. Would you like to provide your own title, or should I generate one for you based on the premise:\n- Generate for me\n- Provide my own",
                "data": collected_inputs,
                "last_question": "title_choice"
            }
        else:
            return {
                "status": "invalid_input",
                "message": "That's not a valid age group. Please choose from 'Kids', 'Teens', 'Adults', or 'Seniors'.",
                "data": collected_inputs,
                "last_question": "age_group"
            }


class ValidateAndUpdateTitleChoiceTool(BaseTool):
    name: str = "Validate and Update Title Choice"
    description: str = "Use this tool to validate the user's choice for title generation (generate or provide own) and update the collected inputs."
    args_schema: Type[BaseModel] = UserInputAndCollectedInputsInput

    def _run(self, user_input: str, collected_inputs: Dict[str, Any]) -> Dict[str, Any]:
        title_choice = _parse_user_input(user_input)
        if _is_valid_title_choice(title_choice):
            collected_inputs["title_choice"] = title_choice
            if title_choice == "Provide my own":
                return {
                    "status": "continue",
                    "message": "Please provide the title for your story.",
                    "data": collected_inputs,
                    "last_question": "title_input"
                }
            else: # Generate for me
                collected_inputs["title_input"] = "" # Ensure it's empty if generating
                return {
                    "status": "continue",
                    "message": "Perfect. How many main characters will be in your story? Please enter a number between 1 and 5.",
                    "data": collected_inputs,
                    "last_question": "num_characters"
                }
        else:
            return {
                "status": "invalid_input",
                "message": "That's not a valid choice. Please choose 'Generate for me' or 'Provide my own'.",
                "data": collected_inputs,
                "last_question": "title_choice"
            }

class ValidateAndUpdateTitleInputTool(BaseTool):
    name: str = "Validate and Update Title Input"
    description: str = "Use this tool to validate the user's provided story title and update the collected inputs."
    args_schema: Type[BaseModel] = UserInputAndCollectedInputsInput

    def _run(self, user_input: str, collected_inputs: Dict[str, Any]) -> Dict[str, Any]:
        title_input = _parse_user_input(user_input)
        if title_input:
            collected_inputs["title_input"] = title_input
            return {
                "status": "continue",
                "message": "Perfect. How many main characters will be in your story? Please enter a number between 1 and 5.",
                "data": collected_inputs,
                "last_question": "num_characters"
            }
        else:
            return {
                "status": "invalid_input",
                "message": "Please provide a title for your story.",
                "data": collected_inputs,
                "last_question": "title_input"
            }

class ValidateAndUpdateNumCharactersTool(BaseTool):
    name: str = "Validate and Update Number of Characters"
    description: str = "Use this tool to validate the user's input for the number of characters and update the collected inputs."
    args_schema: Type[BaseModel] = UserInputAndCollectedInputsInput

    def _run(self, user_input: str, collected_inputs: Dict[str, Any]) -> Dict[str, Any]:
        if _is_valid_num_characters(user_input):
            collected_inputs["num_characters"] = int(user_input)
            return {
                "status": "continue",
                "message": "Great! Would you like me to generate names for your characters, or will you provide them?\n- Generate for me\n- Provide my own",
                "data": collected_inputs,
                "last_question": "name_choice"
            }
        else:
            return {
                "status": "invalid_input",
                "message": "That's not a valid number. Please enter a number between 1 and 5.",
                "data": collected_inputs,
                "last_question": "num_characters"
            }


class ValidateAndUpdateNameChoiceTool(BaseTool):
    name: str = "Validate and Update Name Choice"
    description: str = "Use this tool to validate the user's choice for character name generation (generate or provide own) and update the collected inputs. This tool also triggers name generation if chosen."
    args_schema: Type[BaseModel] = UserInputAndCollectedInputsInput

    def _run(self, user_input: str, collected_inputs: Dict[str, Any]) -> Dict[str, Any]:
        name_choice = _parse_user_input(user_input)
        if _is_valid_name_choice(name_choice):
            collected_inputs["name_choice"] = name_choice
            if name_choice == "Provide my own":
                return {
                    "status": "continue",
                    "message": f"Please provide {collected_inputs.get('num_characters', 0)} character names, separated by commas.",
                    "data": collected_inputs,
                    "last_question": "character_names_input"
                }
            else: # Generate for me
                premise = collected_inputs.get("premise", "")
                age_group = collected_inputs.get("age_group", "")
                num_characters = collected_inputs.get("num_characters", 0)
                
                if premise and age_group and num_characters > 0:
                    generated_names = generate_character_names(_llm_for_tools, premise, age_group, num_characters)
                    collected_inputs["character_names_input"] = generated_names
                    return {
                        "status": "complete",
                        "message": f"Excellent! I have all the information I need. I've generated names: {', '.join(generated_names)}. I will now start weaving your story concept.",
                        "data": collected_inputs
                    }
                else:
                    return {
                        "status": "error", # Should not happen if previous steps are valid
                        "message": "An internal error occurred during name generation setup. Please restart.",
                        "data": collected_inputs
                    }
        else:
            return {
                "status": "invalid_input",
                "message": "That's not a valid choice. Please choose 'Generate for me' or 'Provide my own'.",
                "data": collected_inputs,
                "last_question": "name_choice"
            }

class ValidateAndUpdateCharacterNamesInputTool(BaseTool):
    name: str = "Validate and Update Character Names Input"
    description: str = "Use this tool to validate the user's provided character names and update the collected inputs."
    args_schema: Type[BaseModel] = UserInputAndCollectedInputsInput

    def _run(self, user_input: str, collected_inputs: Dict[str, Any]) -> Dict[str, Any]:
        num_characters = collected_inputs.get("num_characters", 0)
        parsed_names = _parse_character_names_input(user_input, num_characters)
        if parsed_names:
            collected_inputs["character_names_input"] = parsed_names
            return {
                "status": "complete",
                "message": "Excellent! I have all the information I need. I will now start weaving your story concept.",
                "data": collected_inputs
            }
        else:
            return {
                "status": "invalid_input",
                "message": f"Please provide exactly {num_characters} names, separated by commas.",
                "data": collected_inputs,
                "last_question": "character_names_input"
            }

class SignalCompletionTool(BaseTool):
    name: str = "Signal Completion"
    description: str = "Use this tool when all necessary story details (premise, age group, title choice, title input, number of characters, name choice, character names input) have been successfully collected and validated."
    args_schema: Type[BaseModel] = CollectedInputsInput

    def _run(self, collected_inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "complete",
            "message": "Excellent! I have all the information I need. I will now start weaving your story concept.",
            "data": collected_inputs
        }