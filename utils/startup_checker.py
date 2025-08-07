# utils/startup_checker.py
# This module performs startup checks to ensure the environment is correctly configured

import os
import sys
import requests
from dotenv import load_dotenv

def check_env_vars():
    """Loads environment variables from .env file and validates required Langsmith configurations.

    Exits the program if any required environment variables are missing.
    """
    if not load_dotenv():
        print("Error: .env file not found.")
        print("Please create a .env file in the root directory.")
        sys.exit(1)

    required_keys = ["LANGSMITH_API_KEY", "LANGSMITH_PROJECT", "LANGSMITH_ENDPOINT"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        print(f"Error: Missing required environment variables: {', '.join(missing_keys)}")
        print("Please ensure your .env file contains all necessary keys.")
        sys.exit(1)

    os.environ["LANGSMITH_TRACING_V2"] = os.getenv("LANGSMITH_TRACING_V2", "true")
    os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
    print("Environment variables are configured correctly.")

def check_ollama_server():
    """Checks if the Ollama server is running and accessible.

    The Ollama base URL is retrieved from environment variables. Exits the program
    if the server is not reachable.
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        response = requests.get(base_url, timeout=5) # Added a 5-second timeout
        response.raise_for_status()
        print(f"Ollama server is running and accessible at {base_url}.")
    except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
        print(f"Error: Could not connect to Ollama server at {base_url}.")
        print("Please ensure the Ollama server is running.")
        print("You can start it by running `ollama serve` in your terminal.")
        sys.exit(1)

def run_startup_checks():
    """Runs all necessary startup checks for the application.

    This includes validating environment variables and checking Ollama server connectivity.
    """
    check_env_vars()
    check_ollama_server()
