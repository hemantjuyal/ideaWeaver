# utils/llm_loader.py
# This module loads the LLM based on the LLM_PROVIDER environment variable.

import os
from crewai import LLM

def load_llm():
    """Loads the LLM (Large Language Model) based on the LLM_PROVIDER environment variable.

    Supports 'OLLAMA' for local Ollama models and 'GEMINI' for Google Gemini API.

    Returns:
        LLM: An instance of the CrewAI LLM or Langchain ChatGoogleGenerativeAI.
    """
    llm_provider = os.getenv("LLM_PROVIDER")

    if llm_provider == "OLLAMA":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model_name = os.getenv("OLLAMA_MODEL", "ollama/gemma3n:latest")
        return LLM(model=model_name, base_url=base_url)
    elif llm_provider == "GEMINI":
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        # Get the model name without the "models/" prefix
        raw_gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
        if raw_gemini_model.startswith("models/"):
            raw_gemini_model = raw_gemini_model.replace("models/", "")

        # Construct the model string in the "provider/model-name" format
        formatted_gemini_model = f"gemini/{raw_gemini_model}"

        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set when LLM_PROVIDER is GEMINI.")

        # Directly initialize crewai.LLM with api_key and formatted model name
        return LLM(
            api_key=gemini_api_key,
            model=formatted_gemini_model,
            temperature=0.7 # Keep temperature if it's a common setting
        )
    else:
        raise ValueError("LLM_PROVIDER environment variable not set or has an unsupported value. Set to 'OLLAMA' or 'GEMINI'.")
