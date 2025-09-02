# utils/llm_loader.py
# This module loads the local LLM via Ollama for the application.

import os
from crewai import LLM

def load_llm():
    """Loads the local LLM (Large Language Model) via Ollama.

    The base URL for Ollama and the model name are retrieved from environment variables.

    Returns:
        LLM: An instance of the CrewAI LLM configured for Ollama.
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("OLLAMA_MODEL", "ollama/gemma3n:latest")
    return LLM(model=model_name, base_url=base_url)
