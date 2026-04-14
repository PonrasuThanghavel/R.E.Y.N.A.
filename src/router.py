import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from tools import TOOL_REGISTRY
from .schema import ActionSchema
from .memory import memory
import json


def route_action(action_obj: ActionSchema):
    action_name = action_obj.action
    params = action_obj.parameters
    risk_level = action_obj.risk_level

    if action_name == "unknown":
        print(
            f"REYNA: I don't have a specific tool for that right now. (Query: {params.get('query')})"
        )
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

    except Exception as e:
        print(f"[Error: Execution] Tool {action_name} failed: {e}")
        memory.append("system", f"Tool {action_name} failed with error: {e}")
