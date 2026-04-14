import datetime
from typing import Any


class MemorySystem:
    def __init__(self):
        self.history = []
        self.context = {}

    def append(self, role: str, content: str):
        self.history.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )

    def set(self, key: str, value: Any):
        self.context[key] = {
            "value": value,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def get(self, key: str) -> Any:
        entry = self.context.get(key)
        return entry["value"] if entry else None

    def get_context_string(self) -> str:
        # returns the recent history to feed to LLM
        if not self.history:
            return "No previous context."
        context_str = "Recent Interaction History:\n"
        for entry in self.history[-10:]:  # keep last 10
            context_str += f"{entry['role'].capitalize()}: {entry['content']}\n"
        return context_str.strip()


# Global memory instance
memory = MemorySystem()
