import json
import subprocess

def test_call():
    try:
        result = subprocess.run(
            ["openclaw", "agent", "--agent", "main", "--json", "-m", "Respond strictly with JSON: {\"hello\": \"world\"}"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        print("Success:", data.get("finalAssistantVisibleText"))
    except Exception as e:
        print("Failed:", e)
test_call()
