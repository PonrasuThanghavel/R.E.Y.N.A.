import subprocess
import tempfile
import os


def execute_code(language: str, code: str, **kwargs) -> dict:
    """Execute code locally."""
    print(f"[Tool: Execute Code] Executing {language} code...")

    if language.lower() not in ["python", "python3"]:
        return {
            "error": f"Language {language} is not supported. Only python is supported for now."
        }

    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        temp_file_path = f.name

    try:
        result = subprocess.run(
            ["python", temp_file_path],
            capture_output=True,
            text=True,
            timeout=10,  # 10 seconds timeout for safety
        )
        return {"stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
