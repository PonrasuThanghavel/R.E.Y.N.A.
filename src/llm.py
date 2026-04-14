"""LLM integration and action generation module.

Handles communication with language models (Ollama/OpenClaw) for generating
structured actions based on user input and context.
"""

import json
import os
from typing import Optional

import requests
from dotenv import load_dotenv
from pydantic import ValidationError

from .reyna_bridge import bridge
from .schema import ActionSchema

load_dotenv()

# =========================
# CONFIG
# =========================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:0.5b")
USE_REYNA_BRIDGE = os.getenv("USE_REYNA_BRIDGE", "true").lower() == "true"

MAX_RETRIES = 2
REQUEST_TIMEOUT = 60

# Block obvious dangerous patterns (basic guardrail)
BLOCKED_PATTERNS = [
    "rm -rf",
    "os.system",
    "subprocess",
    "delete all",
]

# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """You are REYNA, an autonomous agent.

Output STRICT JSON only. No markdown. No explanations.

Schema:
{
  "action": "string",
  "parameters": {},
  "risk_level": "safe | medium | dangerous"
}

Rules:
- Map user intent to closest action
- If no tool applies → action="unknown"
- NEVER include code execution unless explicitly requested
- NEVER generate unsafe/destructive commands
"""


# =========================
# PUBLIC API
# =========================
def generate_action(user_input: str, context: str) -> Optional[ActionSchema]:
    """Generate validated action with retries and fallback.

    Args:
        user_input: User query string.
        context: Context information.

    Returns:
        ActionSchema or None if generation fails.
    """

    for attempt in range(MAX_RETRIES):
        try:
            # Try bridge first
            if USE_REYNA_BRIDGE and bridge.is_connected():
                action = _generate_action_via_bridge(user_input, context)
                if action:
                    return action

            # Fallback to Ollama
            action = _generate_action_via_ollama(user_input, context)
            if action:
                return action

        except (ValueError, ConnectionError, TimeoutError) as e:
            _log_error(f"[Retry {attempt}] Unexpected error: {e}")

    # Final fallback → safe unknown action
    return ActionSchema(
        action="unknown",
        parameters={"query": user_input},
        risk_level="safe",
    )


# =========================
# BRIDGE MODE
# =========================
def _generate_action_via_bridge(
    user_input: str, context: str
) -> Optional[ActionSchema]:
    """Generate action via OpenClaw Reyna bridge.

    Args:
        user_input: User query.
        context: Context information.

    Returns:
        ActionSchema or None if bridge call fails.
    """
    try:
        prompt = _build_prompt(user_input, context)

        response = bridge.ask_reyna(
            prompt,
            metadata={"type": "action_generation"},
        )

        if not response:
            return None

        parsed = _safe_parse_json(response)
        return _validate_action(parsed)

    except (ValueError, IOError, OSError) as e:
        _log_error(f"[Bridge] {e}")
        return None


# =========================
# OLLAMA MODE
# =========================
def _generate_action_via_ollama(
    user_input: str, context: str
) -> Optional[ActionSchema]:
    """Generate action via Ollama LLM.

    Args:
        user_input: User query.
        context: Context information.

    Returns:
        ActionSchema or None if Ollama call fails.
    """
    try:
        prompt = _build_prompt(user_input, context)

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.0,
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        output = response.json().get("response", "").strip()

        if not output:
            raise ValueError("Empty LLM response")

        parsed = _safe_parse_json(output)
        return _validate_action(parsed)

    except requests.exceptions.Timeout:
        _log_error("[Ollama] Timeout")
    except requests.exceptions.ConnectionError:
        _log_error("[Ollama] Connection failed")
    except (ValueError, KeyError) as e:
        _log_error(f"[Ollama] {e}")

    return None


# =========================
# HELPERS
# =========================
def _build_prompt(user_input: str, context: str) -> str:
    """Build sanitized LLM prompt.

    Args:
        user_input: User query.
        context: Context information.

    Returns:
        Formatted prompt string.
    """
    return f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser:\n{user_input}\n\nJSON:"


def _safe_parse_json(text: str) -> dict:
    """Extract and parse JSON safely from LLM output.

    Args:
        text: Raw text from LLM.

    Returns:
        Parsed dictionary.

    Raises:
        ValueError: If JSON parsing fails.
    """
    try:
        # Remove markdown if present
        if "```" in text:
            text = text.split("```")[1].strip()

        return json.loads(text)

    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON from LLM:\n{text}") from exc


def _validate_action(data: dict) -> Optional[ActionSchema]:
    """Validate action schema and apply security filters.

    Args:
        data: Raw action dictionary.

    Returns:
        Validated ActionSchema or None if validation fails.
    """
    try:
        action = ActionSchema(**data)

        # Security: block dangerous patterns
        if action.action == "execute_code":
            code = action.parameters.get("code", "")
            if any(p in code.lower() for p in BLOCKED_PATTERNS):
                raise ValueError("Blocked dangerous code pattern")

        return action

    except ValidationError as e:
        _log_error(f"[Schema] {e}")
    except ValueError as e:
        _log_error(f"[Security] {e}")

    return None


def _log_error(msg: str) -> None:
    """Log error message. Replace with structured logging later.

    Args:
        msg: Error message to log.
    """
    print(f"[ERROR] {msg}")
