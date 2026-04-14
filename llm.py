import json
import requests
from schema import ActionSchema
from pydantic import ValidationError

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

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
"""

def generate_action(user_input: str, context: str) -> ActionSchema:
    prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nUser: {user_input}\nREYNA Action (JSON only):"

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json" # Ollama json format constraint (if supported, else we just rely on prompt)
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        output_text = data.get("response", "").strip()

        # Parse JSON and validate
        parsed_json = json.loads(output_text)
        action_obj = ActionSchema(**parsed_json)
        return action_obj
        
    except requests.exceptions.RequestException as e:
        print(f"[Error: LLM Connection] Could not connect to Ollama. {e}")
        return None
    except json.JSONDecodeError:
        print(f"[Error: Decision Layer] LLM did not output valid JSON. Raw output:\n{output_text}")
        return None
    except ValidationError as e:
        print(f"[Error: Decision Layer] LLM output didn't match schema:\n{e}")
        return None
