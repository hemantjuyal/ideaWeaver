import os
import requests
import logging
import json

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def call_master_agent_api(conversation_history, user_input, collected_inputs):
    try:
        response = requests.post(
            f"{API_BASE_URL}/converse",
            json={
                "conversation_history": conversation_history,
                "user_input": user_input,
                "collected_inputs": collected_inputs
            }
        )
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API call to master agent failed: {e}", exc_info=True)
        return {"status": "error", "message": "Failed to connect to the Master Agent. Please ensure the API server is running."}
    except json.JSONDecodeError:
        logging.error(f"Master agent API returned invalid JSON.", exc_info=True)
        return {"status": "error", "message": "Master Agent returned an unreadable response."}

def call_generate_story_api(collected_inputs):
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate_story",
            json=collected_inputs
        )
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API call to story generation failed: {e}", exc_info=True)
        return {"status": "error", "message": "Failed to connect to the Story Generation API. Please ensure the API server is running."}
    except json.JSONDecodeError:
        logging.error(f"Story Generation API returned invalid JSON.", exc_info=True)
        return {"status": "error", "message": "Story Generation API returned an unreadable response."}
