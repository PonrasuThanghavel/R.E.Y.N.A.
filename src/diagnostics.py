#!/usr/bin/env python3
"""Diagnostics tool for system health and bridge connectivity checks.

Verifies system configuration and connectivity to external services.
"""

import json
import sys
from pathlib import Path
from .reyna_bridge import bridge


def check_bridge_status():
    """Check OpenClaw Reyna bridge connectivity."""
    print("\n" + "=" * 60)
    print("OpenClaw Reyna Bridge Status")
    print("=" * 60)

    connected = bridge.is_connected()
    workspace_dir = Path.home() / ".openclaw" / "workspace"
    status_file = workspace_dir / ".reyna_bridge_status"

    if not status_file.exists():
        print("❌ Bridge status file not found")
        print(f"   Expected: {status_file}")
        return False

    try:
        status = json.loads(status_file.read_text())
        print(f"Status: {'🟢 Connected' if connected else '🔴 Disconnected'}")
        print(f"Session: {status.get('session', 'N/A')}")
        print(f"PID: {status.get('pid', 'N/A')}")
        print(f"Details: {json.dumps(status, indent=2)}")

        return connected
    except Exception as e:
        print(f"❌ Error reading status: {e}")
        return False


def check_ollama():
    """Check if local Ollama is running."""
    print("\n" + "=" * 60)
    print("Local Ollama Status")
    print("=" * 60)

    import requests
    from dotenv import load_dotenv
    import os

    load_dotenv()

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "mistral")

    print(f"URL: {ollama_url}")
    print(f"Model: {ollama_model}")

    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("\n✓ Ollama is running")
            print(f"  Available models: {len(models)}")
            for model in models[:5]:
                print(f"    • {model.get('name', 'unknown')}")

            # Check if requested model is available
            model_names = [m.get("name", "") for m in models]
            if any(ollama_model in name for name in model_names):
                print(f"\n  ✓ Model '{ollama_model}' is installed")
                return True
            else:
                print(f"\n  ⚠️  Model '{ollama_model}' not found")
                print(f"     Install with: ollama pull {ollama_model}")
                return False
        else:
            print(f"❌ Ollama returned error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Ollama at {ollama_url}")
        print("   Start Ollama with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_bridge_communication():
    """Test if bridge can communicate with Reyna."""
    print("\n" + "=" * 60)
    print("Bridge Communication Test")
    print("=" * 60)

    if not bridge.is_connected():
        print("❌ Bridge not connected - cannot test")
        return False

    try:
        print("Sending test message to Reyna via bridge...")
        # Send a simple JSON generation test
        test_prompt = '{"test": "message", "request": "Respond with: {\\"status\\": \\"success\\"}"}'

        response = bridge.ask_reyna(test_prompt)

        if response:
            print("✓ Response received")
            print(f"  Length: {len(response)} chars")
            print(f"  Preview: {response[:100]}...")
            return True
        else:
            print("❌ No response (timeout)")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all diagnostics."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "R.E.Y.N.A. System Diagnostics".center(38) + " " * 10 + "║")
    print("╚" + "═" * 58 + "╝")

    bridge_ok = check_bridge_status()
    olama_ok = check_ollama()

    if bridge_ok:
        comm_ok = test_bridge_communication()
    else:
        comm_ok = False

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    systems = [
        ("OpenClaw Reyna Bridge", bridge_ok),
        ("Local Ollama", olama_ok),
        ("Bridge Communication", comm_ok if bridge_ok else None),
    ]

    for name, status in systems:
        if status is None:
            icon = "⊘"
        elif status:
            icon = "✓"
        else:
            icon = "✗"
        print(f"{icon} {name}")

    print("\n" + "=" * 60)

    if bridge_ok and comm_ok:
        print("✓ System ready: Using OpenClaw Reyna bridge")
        return 0
    elif olama_ok:
        print("✓ System ready: Using local Ollama fallback")
        return 0
    else:
        print("❌ System not ready: Check errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
