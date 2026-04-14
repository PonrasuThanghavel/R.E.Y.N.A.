#!/usr/bin/env python3
"""
Test R.E.Y.N.A. with OpenClaw Reyna Bridge (force bridge mode)
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm import generate_action
from memory import memory

# Force use of bridge
os.environ["USE_REYNA_BRIDGE"] = "true"

# Reload the module to pick up env change
import importlib
import llm

importlib.reload(llm)
from llm import generate_action

print("=" * 60)
print("Testing R.E.Y.N.A. with OpenClaw Reyna Bridge")
print("=" * 60)

test_cases = ["What's the weather in Tokyo?", "hi there", "Tell me a joke"]

for user_input in test_cases:
    print(f"\n🗣️  User: {user_input}")
    print("-" * 40)

    memory.append("user", user_input)
    context = memory.get_context_string()

    try:
        print("Sending to bridge...")
        # Set a shorter timeout for testing
        action = generate_action(user_input, context)

        if action:
            print(f"✓ Bridge responded!")
            print(f"  Action: {action.action}")
            print(f"  Risk: {action.risk_level}")
            print(f"  Params: {action.parameters}")
        else:
            print(f"❌ No action generated")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
