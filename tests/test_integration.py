#!/usr/bin/env python3
"""
Test script to verify OpenClaw integration with Kimi-2.5-k2
This script validates that the LLM integration is working correctly.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm import generate_action


def test_openclaw_integration():
    """Test the OpenClaw integration with sample inputs."""

    print("=" * 60)
    print("OpenClaw Integration Test for Kimi-2.5-k2")
    print("=" * 60)

    test_cases = [
        {
            "name": "Weather Query",
            "user_input": "What's the weather in San Francisco?",
            "context": "No previous context.",
            "expected_action": "get_weather",
        },
        {
            "name": "Unknown Query",
            "user_input": "Tell me a joke",
            "context": "No previous context.",
            "expected_action": "unknown",
        },
        {
            "name": "Code Execution",
            "user_input": "Execute a Python script that prints hello world",
            "context": "No previous context.",
            "expected_action": "execute_code",
        },
    ]

    results = []

    for idx, test in enumerate(test_cases, 1):
        print(f"\n[Test {idx}] {test['name']}")
        print(f"Input: {test['user_input']}")
        print("-" * 40)

        try:
            action = generate_action(test["user_input"], test["context"])

            if action:
                print(f"✓ Success!")
                print(f"  Action: {action.action}")
                print(f"  Risk Level: {action.risk_level}")
                print(f"  Parameters: {json.dumps(action.parameters, indent=4)}")
                results.append(
                    {"test": test["name"], "status": "pass", "action": action.action}
                )
            else:
                print(f"✗ Failed - No action returned")
                results.append({"test": test["name"], "status": "fail", "action": None})

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            results.append({"test": test["name"], "status": "error", "error": str(e)})

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] != "pass")

    for result in results:
        status_icon = "✓" if result["status"] == "pass" else "✗"
        print(f"{status_icon} {result['test']}: {result['status'].upper()}")

    print(f"\nTotal: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = test_openclaw_integration()
    sys.exit(0 if success else 1)
