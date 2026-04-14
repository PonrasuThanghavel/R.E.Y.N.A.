"""Action routing and tool execution module.

Responsible for routing generated actions to appropriate tools with safety checks.
"""

import json
import sys
from pathlib import Path

from tools import TOOL_REGISTRY

from .schema import ActionSchema
from .memory import memory

sys.path.insert(0, str(Path(__file__).parent.parent))


def route_action(action_obj: ActionSchema):
    """Route and execute an action with safety checks.
    
    Args:
        action_obj: The action to route and execute.
    """
    action_name = action_obj.action
    params = action_obj.parameters
    risk_level = action_obj.risk_level

    if action_name == "unknown":
        query = params.get('query', 'unknown')
        print(f"REYNA: I don't have a specific tool for that right now. (Query: {query})")
        memory.append("reyna", str(params))
        return

    # Safety Layer Check
    if risk_level in ["medium", "dangerous"]:
        print(f"\n[Safety Alert] This action is classified as '{risk_level.upper()}'.")
        print(f"Tool: {action_name}")
        print(f"Params: {json.dumps(params, indent=2)}")

        confirmation = input("Do you wish to proceed? (y/N): ").strip().lower()
        if confirmation != "y":
            print("[System] Action cancelled by user.")
            memory.append("reyna", "[Safety] Action blocked by user.")
            return

    # Tools Layer Execution
    handler = TOOL_REGISTRY.get(action_name)
    if not handler:
        print(f"[Error: Route] Tool '{action_name}' is not registered.")
        memory.append("reyna", f"Attempted to use nonexistent tool {action_name}")
        return

    try:
        print(f"[System] Executing {action_name}...")
        result = handler(**params)
        print(f"[Result] {json.dumps(result, indent=2)}")

        # Memory update
        memory.append("reyna", f"Executed {action_name}. Result: {result}")

    except (KeyError, TypeError, ValueError) as exc:
        error_msg = f"Tool {action_name} failed: {exc}"
        print(f"[Error: Execution] {error_msg}")
        memory.append("system", error_msg)
