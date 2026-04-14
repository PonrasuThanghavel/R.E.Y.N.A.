"""Memory system with vector storage and semantic search.

Manages short-term history, context, and vector embeddings for semantic memory.
"""

import datetime
from typing import Any, List

import chromadb
from sentence_transformers import SentenceTransformer


class MemorySystem:
    """Memory system with vector storage and semantic search.

    Combines short-term history, context key-value store, and vector embeddings
    for intelligent context retrieval.
    """

    def __init__(self):
        # Short-term memory
        self.history = []

        # Key-value memory
        self.context = {}

        # Vector DB setup
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("reyna_memory")

        # Embedding model (lightweight)
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        self.max_history = 20

    # =========================
    # SHORT-TERM MEMORY
    # =========================
    def append(self, role: str, content: str):
        timestamp = datetime.datetime.now().isoformat()

        entry = {
            "role": role,
            "content": content,
            "timestamp": timestamp,
        }

        self.history.append(entry)

        # Keep history bounded
        if len(self.history) > self.max_history:
            self.history.pop(0)

        # Store in vector DB for long-term recall
        self._store_vector(content, metadata={"role": role, "timestamp": timestamp})

    # =========================
    # VECTOR STORAGE
    # =========================
    def _store_vector(self, text: str, metadata: dict):
        embedding = self.embedder.encode(text).tolist()

        self.collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[f"{metadata['timestamp']}"],
        )

    def _search_vectors(self, query: str, k: int = 3) -> List[str]:
        embedding = self.embedder.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=k,
        )

        return results.get("documents", [[]])[0]

    # =========================
    # KEY-VALUE MEMORY
    # =========================
    def set(self, key: str, value: Any):
        self.context[key] = {
            "value": value,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def get(self, key: str) -> Any:
        entry = self.context.get(key)
        return entry["value"] if entry else None

    # =========================
    # CONTEXT BUILDING (SMART)
    # =========================
    def get_context_string(self, query: str = "") -> str:
        context_parts = []

        # Recent history
        if self.history:
            context_parts.append("Recent Conversation:")
            for entry in self.history[-5:]:
                context_parts.append(
                    f"{entry['role'].capitalize()}: {entry['content']}"
                )

        # Semantic memory (important!)
        if query:
            similar_memories = self._search_vectors(query)

            if similar_memories:
                context_parts.append("\nRelevant Past Memories:")
                for mem in similar_memories:
                    context_parts.append(f"- {mem}")

        return "\n".join(context_parts) if context_parts else "No context."

    # =========================
    # OPTIONAL CLEANUP
    # =========================
    def clear(self):
        self.history.clear()
        self.context.clear()
        self.client.delete_collection("reyna_memory")
        self.collection = self.client.create_collection("reyna_memory")


# Global instance
memory = MemorySystem()
