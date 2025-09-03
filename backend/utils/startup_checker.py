# utils/startup_checker.py
# This module performs startup checks to ensure the environment is correctly configured

import os
import sys
import requests
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_env_vars():
    """Loads environment variables from .env file and validates required configurations based on LLM_PROVIDER.

    Returns:
        bool: True if environment variables are configured, False otherwise.
    """
    if not load_dotenv():
        logging.error("Error: .env file not found.")
        logging.error("Please create a .env file in the root directory.")
        return False

    required_keys = ["LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_ENDPOINT", "LLM_PROVIDER"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        logging.error(f"Error: Missing required environment variables: {', '.join(missing_keys)}")
        logging.error("Please ensure your .env file contains all necessary keys.")
        return False

    llm_provider = os.getenv("LLM_PROVIDER")
    if llm_provider == "OLLAMA":
        llm_required_keys = ["OLLAMA_BASE_URL", "OLLAMA_MODEL"]
    elif llm_provider == "GEMINI":
        llm_required_keys = ["GEMINI_API_KEY", "GEMINI_MODEL"]
    else:
        logging.error(f"Error: Unsupported LLM_PROVIDER: {llm_provider}. Must be 'OLLAMA' or 'GEMINI'.")
        return False

    missing_llm_keys = [key for key in llm_required_keys if not os.getenv(key)]
    if missing_llm_keys:
        logging.error(f"Error: Missing required LLM environment variables for {llm_provider}: {', '.join(missing_llm_keys)}")
        logging.error("Please ensure your .env file contains all necessary keys for the chosen LLM_PROVIDER.")
        return False

    os.environ["LANGSMITH_TRACING_V2"] = os.getenv("LANGSMITH_TRACING_V2", "true")
    os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
    logging.info("Environment variables are configured correctly.")
    return True

def check_ollama_server():
    """Checks if the Ollama server is running and accessible.

    The Ollama base URL is retrieved from environment variables.

    Returns:
        bool: True if the server is running, False otherwise.
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        response = requests.get(base_url, timeout=5)
        response.raise_for_status()
        logging.info(f"Ollama server is running and accessible at {base_url}.")
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
        logging.error(f"Error: Could not connect to Ollama server at {base_url}.")
        logging.error("Please ensure the Ollama server is running.")
        logging.error("You can start it by running `ollama serve` in your terminal.")
        return False

def run_frontend_startup_checks():
    """Runs all necessary startup checks for the frontend application.

    Returns:
        bool: True if all checks pass, False otherwise.
    """
    logging.info("--- Running Frontend Startup Checks ---")
    env_vars_ok = check_env_vars()
    if not env_vars_ok:
        logging.error("Frontend startup checks failed.")
        return False

    llm_provider = os.getenv("LLM_PROVIDER")
    if llm_provider == "OLLAMA":
        ollama_ok = check_ollama_server()
        if not ollama_ok:
            logging.error("Frontend startup checks failed.")
            return False

    logging.info("--- Frontend Startup Checks Passed ---")
    return True

def run_backend_startup_checks():
    """Runs all necessary startup checks for the backend application.

    Exits the program if any checks fail.
    """
    logging.info("--- Running Backend Startup Checks ---")
    env_vars_ok = check_env_vars()
    if not env_vars_ok:
        logging.error("Backend startup checks failed. Exiting.")
        sys.exit(1)
    logging.info("--- Backend Startup Checks Passed ---")