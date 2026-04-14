#!/usr/bin/env python3
"""
Quick test to verify llm.py generates proper ActionSchema
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm import generate_action

print("Testing LLM action generation with lightweight Qwen model...\n")

# Test with a simple message
user_input = "What's the weather?"
context = "No previous context."

print(f"Input: {user_input}")
print(f"Context: {context}")
print("\nGenerating action...")

action = generate_action(user_input, context)

if action is None:
    print("❌ Failed: generate_action returned None")
    sys.exit(1)

print("\n✓ Success!")
print(f"  Type: {type(action).__name__}")
print(f"  Action: {action.action}")
print(f"  Risk Level: {action.risk_level}")
print(f"  Parameters: {action.parameters}")

sys.exit(0)
