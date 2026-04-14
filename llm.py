import os
import json
import requests
from schema import ActionSchema
from pydantic import ValidationError
from dotenv import load_dotenv
from reyna_bridge import bridge

load_dotenv()

# Ollama configuration (running locally)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:0.5b")

# Use OpenClaw Reyna bridge if available, otherwise fallback to local Ollama
USE_REYNA_BRIDGE = os.getenv("USE_REYNA_BRIDGE", "true").lower() == "true"

SYSTEM_PROMPT = """You are REYNA (Retrieval Engine, Yarn & Narrative Assistant), an autonomous agent.
Your primary function is to interpret user input and translate it into a structured JSON action.
The JSON must perfectly match this exact schema:
{
  "action": "string",
  "parameters": {},
  "risk_level": "safe | medium | dangerous"
}

Available actions:
1. `get_weather` - Retrieve weather information. Parameters: {"location": "string"} Risk: "safe"
2. `github_commit` - Commit code to GitHub. Parameters: {"repo": "string", "message": "string"} Risk: "medium"
3. `execute_code` - Execute code locally. Parameters: {"language": "python", "code": "string"} Risk: "dangerous"

You MUST respond ONLY with the JSON document and absolutely no extra text, markdown formatting, or markdown json blocks (e.g. ```json).
Always map the intent to the closest tool. If it's a general question not matching any tool, set action to `unknown`, parameters to `{"query": <input>}`, and risk_level to `safe`.
Respond with strict JSON only.
"""

def generate_action(user_input: str, context: str) -> ActionSchema:
    """
    Generate a structured action using OpenClaw Reyna bridge (if available)
    or fallback to local Ollama model.
    
    Args:
        user_input: The user's input string
        context: Recent conversation context
        
    Returns:
        ActionSchema object or None if generation fails
    """
    
    # Try OpenClaw Reyna bridge first if enabled
    if USE_REYNA_BRIDGE and bridge.is_connected():
        action_obj = _generate_action_via_bridge(user_input, context)
        if action_obj:
            return action_obj
        # Fall through to Ollama if bridge fails
    
    # Fallback to local Ollama
    return _generate_action_via_ollama(user_input, context)


def _generate_action_via_bridge(user_input: str, context: str) -> ActionSchema:
    """Generate action via OpenClaw Reyna bridge."""
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nUser: {user_input}\nREYNA Action (JSON only):"
        
        response = bridge.ask_reyna(
            full_prompt,
            metadata={
                "type": "action_generation",
                "model": "reyna-openclaw"
            }
        )
        
        if not response:
            return None
        
        # Parse JSON response
        try:
            parsed_json = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            parsed_json = json.loads(json_str)
        
        action_obj = ActionSchema(**parsed_json)
        print("[System] Using OpenClaw Reyna bridge")
        return action_obj
        
    except ValidationError as e:
        print(f"[Error: Bridge] LLM output didn't match schema:\n{e}")
        return None
    except Exception as e:
        print(f"[Error: Bridge] Failed to generate action via bridge: {e}")
        return None


def _generate_action_via_ollama(user_input: str, context: str) -> ActionSchema:
    """Generate action via local Ollama model."""
    full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nUser: {user_input}\nREYNA Action (JSON only):"

    try:
        # Call local Ollama API
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": False,
                "temperature": 0.0
            },
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        output_text = data.get("response", "").strip()

        if not output_text:
            print("[Error: Decision Layer] Ollama returned empty response.")
            return None

        # Try to extract JSON from the response
        # Handle cases where model wraps JSON in markdown code blocks
        if "```json" in output_text:
            json_str = output_text.split("```json")[1].split("```")[0].strip()
        elif "```" in output_text:
            json_str = output_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = output_text

        # Parse JSON and validate
        parsed_json = json.loads(json_str)
        action_obj = ActionSchema(**parsed_json)
        print(f"[System] Using local Ollama model: {MODEL_NAME}")
        return action_obj
        
    except requests.exceptions.ConnectionError:
        print(f"[Error: LLM Connection] Could not connect to Ollama at {OLLAMA_BASE_URL}")
        print("Make sure Ollama is running: ollama serve")
        return None
    except requests.exceptions.Timeout:
        print("[Error: LLM Connection] Ollama request timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[Error: LLM Connection] Ollama request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"[Error: Decision Layer] LLM did not output valid JSON. Raw output:\n{output_text}")
        print(f"JSON Error: {e}")
        return None
    except ValidationError as e:
        print(f"[Error: Decision Layer] LLM output didn't match schema:\n{e}")
        return None
    except Exception as e:
        print(f"[Error: LLM] Unexpected error: {e}")
        return None
