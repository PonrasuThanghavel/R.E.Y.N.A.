import json
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any


class ReynaBridge:
    """Secure file-based IPC bridge for OpenClaw Reyna agent."""

    MAX_MESSAGE_SIZE = 10_000  # Prevent abuse (10KB)

    def __init__(self):
        self.workspace_dir = Path.home() / ".openclaw" / "workspace"
        self.request_file = self.workspace_dir / ".reyna_request"
        self.response_file = self.workspace_dir / ".reyna_response"
        self.status_file = self.workspace_dir / ".reyna_bridge_status"

        self.timeout_seconds = 30
        self.poll_interval = 0.1

        # Ensure workspace exists
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    # =========================
    # CONNECTION CHECK
    # =========================
    def is_connected(self) -> bool:
        if not self.status_file.exists():
            return False

        try:
            status = json.loads(self.status_file.read_text())

            is_status_ok = status.get("status") in ["active", "connected", "ready"]
            has_session = "session" in status
            is_ready = status.get("reyna_ready", False)

            return is_status_ok and (has_session or is_ready)

        except Exception:
            return False

    # =========================
    # MAIN IPC METHOD
    # =========================
    def ask_reyna(
        self, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:

        if not self.is_connected():
            return None

        # Input validation
        if not isinstance(message, str) or len(message) > self.MAX_MESSAGE_SIZE:
            raise ValueError("Invalid or oversized message")

        request_id = str(uuid.uuid4())

        try:
            request_data = {
                "id": request_id,
                "message": message,
                "timestamp": time.time(),
                "metadata": metadata or {},
            }

            self._atomic_write(self.request_file, request_data)

            return self._wait_for_response(request_id)

        except Exception as e:
            print(f"[Bridge Error] {e}")
            return None

    # =========================
    # RESPONSE HANDLING
    # =========================
    def _wait_for_response(self, request_id: str) -> Optional[str]:
        poll_count = int(self.timeout_seconds / self.poll_interval)

        for _ in range(poll_count):
            if self.response_file.exists():
                try:
                    data = json.loads(self.response_file.read_text())

                    # Validate request-response match
                    if data.get("id") != request_id:
                        time.sleep(self.poll_interval)
                        continue

                    self.response_file.unlink(missing_ok=True)

                    return data.get("response")

                except json.JSONDecodeError:
                    pass

            time.sleep(self.poll_interval)

        return None

    # =========================
    # TOOL EXECUTION
    # =========================
    def execute_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:

        if not isinstance(parameters, dict):
            raise ValueError("Invalid parameters")

        request = {
            "tool": tool_name,
            "parameters": parameters,
        }

        response = self.ask_reyna(
            json.dumps(request),
            metadata={"type": "tool_request", "tool": tool_name},
        )

        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"result": response}

        return None

    # =========================
    # MEMORY
    # =========================
    def query_memory(self, query: str) -> Optional[str]:
        return self.ask_reyna(
            query,
            metadata={"type": "memory_query"},
        )

    def update_context(self, role: str, content: str) -> bool:
        if role not in ["user", "system", "assistant"]:
            raise ValueError("Invalid role")

        payload = {"role": role, "content": content}

        response = self.ask_reyna(
            json.dumps(payload),
            metadata={"type": "context_update"},
        )

        return response is not None

    # =========================
    # FILE SAFETY
    # =========================
    def _atomic_write(self, path: Path, data: dict):
        """Write file atomically to avoid corruption."""
        temp_file = path.with_suffix(".tmp")
        temp_file.write_text(json.dumps(data))
        temp_file.replace(path)


# Global instance
bridge = ReynaBridge()