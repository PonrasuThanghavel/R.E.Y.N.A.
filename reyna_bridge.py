"""
Reyna Bridge - Connects R.E.Y.N.A. voice assistant to OpenClaw Reyna agent
Uses file-based IPC for reliable inter-process communication
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

class ReynaBridge:
    """File-based bridge to communicate with OpenClaw Reyna agent."""
    
    def __init__(self):
        self.workspace_dir = Path.home() / ".openclaw" / "workspace"
        self.request_file = self.workspace_dir / ".reyna_request"
        self.response_file = self.workspace_dir / ".reyna_response"
        self.status_file = self.workspace_dir / ".reyna_bridge_status"
        self.timeout_seconds = 30
        self.poll_interval = 0.1
        
    def is_connected(self) -> bool:
        """Check if OpenClaw Reyna agent is connected and ready."""
        if not self.status_file.exists():
            return False
        try:
            status = json.loads(self.status_file.read_text())
            # Support multiple status formats
            is_status_ok = status.get("status") in ["active", "connected", "ready"]
            has_session = "session" in status
            is_ready = status.get("reyna_ready", False)
            
            # Connected if status is OK AND (has session OR is explicitly ready)
            return is_status_ok and (has_session or is_ready)
        except Exception:
            return False
    
    def ask_reyna(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Send a message to OpenClaw Reyna agent and wait for response.
        
        Args:
            message: The query or command to send
            metadata: Optional metadata (user context, risk_level, etc.)
            
        Returns:
            Response from Reyna agent or None if timeout
        """
        if not self.is_connected():
            return None
        
        try:
            # Prepare request
            request_data = {
                "message": message,
                "timestamp": time.time(),
                "metadata": metadata or {}
            }
            
            # Write request file
            self.request_file.write_text(json.dumps(request_data, indent=2))
            
            # Wait for response (polling)
            poll_count = int(self.timeout_seconds / self.poll_interval)
            for _ in range(poll_count):
                if self.response_file.exists():
                    try:
                        response_data = json.loads(self.response_file.read_text())
                        # Clean up response file
                        self.response_file.unlink()
                        return response_data.get("response")
                    except json.JSONDecodeError:
                        continue
                time.sleep(self.poll_interval)
            
            # Timeout
            return None
            
        except Exception as e:
            print(f"[Bridge Error] Failed to communicate with Reyna: {e}")
            return None
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute a tool through the OpenClaw Reyna agent.
        
        Args:
            tool_name: Name of the tool (get_weather, github_commit, etc.)
            parameters: Tool parameters
            
        Returns:
            Tool execution result or None if failed
        """
        message = f"Execute tool: {tool_name} with params: {json.dumps(parameters)}"
        response = self.ask_reyna(message, metadata={"type": "tool_request", "tool": tool_name})
        
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"result": response}
        return None
    
    def query_memory(self, query: str) -> Optional[str]:
        """Query Reyna's memory system."""
        message = f"Query memory: {query}"
        return self.ask_reyna(message, metadata={"type": "memory_query"})
    
    def update_context(self, role: str, content: str) -> bool:
        """Update Reyna's context with new interaction."""
        message = f"Update context - {role}: {content}"
        response = self.ask_reyna(message, metadata={"type": "context_update"})
        return response is not None


# Global bridge instance
bridge = ReynaBridge()
