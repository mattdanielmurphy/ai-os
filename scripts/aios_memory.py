#!/usr/bin/env python3
"""
aios_memory.py — Unified Battle-Tested Memory Engine for AI-OS (backed by Mem0 & SQLite).

Provides semantic recall, fact ingestion, pre-flight hydration, and sync between
Hermes memories and Mem0 vector store.

Usage:
  python3 scripts/aios_memory.py add "User prefers bun over npm/pnpm" --category tooling
  python3 scripts/aios_memory.py search "package manager preferences"
  python3 scripts/aios_memory.py prefetch "implementing a build script"
  python3 scripts/aios_memory.py list
  python3 scripts/aios_memory.py sync
  python3 scripts/aios_memory.py delete <memory_id>
"""

import os
import sys
import json
import argparse
import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional

# Suppress telemetry and third-party verbose logs
os.environ["MEM0_TELEMETRY"] = "False"
os.environ["POSTHOG_DISABLED"] = "1"
warnings.filterwarnings("ignore")

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).resolve()
MEM0_DIR = HERMES_HOME / "mem0_qdrant"
MEMORY_MD_PATH = HERMES_HOME / "memories" / "MEMORY.md"
DEFAULT_USER_ID = "matt"


def get_mem0_client():
    """Initialize and return a configured Mem0 client instance."""
    # Check if Platform API key exists in environment or ~/.hermes/.env
    api_key = os.environ.get("MEM0_API_KEY")
    if not api_key and (HERMES_HOME / ".env").exists():
        try:
            with open(HERMES_HOME / ".env", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("MEM0_API_KEY="):
                        api_key = line.strip().split("=", 1)[1].strip("\"' ")
                        break
        except Exception:
            pass

    if api_key:
        from mem0 import MemoryClient
        return MemoryClient(api_key=api_key), "platform"

    # OSS Mode: Local Qdrant + fastembed + local/OpenAI LLM
    from mem0 import Memory

    MEM0_DIR.mkdir(parents=True, exist_ok=True)
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "path": str(MEM0_DIR),
                "embedding_model_dims": 384,
            },
        },
        "embedder": {
            "provider": "fastembed",
            "config": {
                "model": "BAAI/bge-small-en-v1.5",
            },
        },
        "llm": {
            "provider": "openai",
            "config": {
                "model": "deepseek-chat",
                "api_key": "dummy",
            },
        },
    }

    try:
        memory = Memory.from_config(config)
        return memory, "oss"
    except Exception as e:
        print(f"[aios-memory] Warning: Failed to init Mem0 OSS backend: {e}", file=sys.stderr)
        return None, "fallback"


def add_memory(text: str, user_id: str = DEFAULT_USER_ID, category: str = "general", source: str = "ai-os") -> Dict[str, Any]:
    """Store a memory into Mem0."""
    client, mode = get_mem0_client()
    if not client:
        return {"status": "error", "message": "Memory engine unavailable"}

    metadata = {"category": category, "source": source}

    try:
        if mode == "platform":
            res = client.add([{"role": "user", "content": text}], user_id=user_id, metadata=metadata, infer=False)
        else:
            res = client.add(text, user_id=user_id, metadata=metadata, infer=False)
        return {"status": "ok", "mode": mode, "result": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def search_memories(query: str, user_id: str = DEFAULT_USER_ID, limit: int = 5) -> List[Dict[str, Any]]:
    """Search memories semantically by query."""
    client, mode = get_mem0_client()
    if not client:
        return []

    try:
        if mode == "platform":
            res = client.search(query, filters={"user_id": user_id}, top_k=limit)
        else:
            res = client.search(query, filters={"user_id": user_id}, limit=limit)

        if isinstance(res, dict):
            return res.get("results", [])
        elif isinstance(res, list):
            return res
        return []
    except Exception as e:
        print(f"[aios-memory] Search error: {e}", file=sys.stderr)
        return []


def prefetch_context(query: str, user_id: str = DEFAULT_USER_ID, limit: int = 5) -> str:
    """Format relevant memories into a clean markdown context block for pre-flight hydration."""
    memories = search_memories(query, user_id=user_id, limit=limit)
    if not memories:
        return ""

    lines = ["### 🧠 Relevant Recalled Context & Memories (Mem0):"]
    for m in memories:
        text = m.get("memory", "").strip()
        if text:
            score = m.get("score")
            score_str = f" *(relevance: {score:.2f})*" if score is not None else ""
            lines.append(f"- {text}{score_str}")

    return "\n".join(lines)


def list_memories(user_id: str = DEFAULT_USER_ID) -> List[Dict[str, Any]]:
    """List all memories for a user."""
    client, mode = get_mem0_client()
    if not client:
        return []

    try:
        if mode == "platform":
            res = client.get_all(filters={"user_id": user_id})
        else:
            res = client.get_all(filters={"user_id": user_id})

        if isinstance(res, dict):
            return res.get("results", [])
        elif isinstance(res, list):
            return res
        return []
    except Exception as e:
        print(f"[aios-memory] List error: {e}", file=sys.stderr)
        return []


def delete_memory(memory_id: str) -> Dict[str, Any]:
    """Delete a memory by ID."""
    client, mode = get_mem0_client()
    if not client:
        return {"status": "error", "message": "Memory engine unavailable"}

    try:
        client.delete(memory_id=memory_id)
        return {"status": "ok", "deleted_id": memory_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def sync_from_hermes_memory_md(user_id: str = DEFAULT_USER_ID) -> int:
    """Sync existing durable facts from ~/.hermes/memories/MEMORY.md into Mem0."""
    if not MEMORY_MD_PATH.exists():
        print(f"No MEMORY.md found at {MEMORY_MD_PATH}", file=sys.stderr)
        return 0

    with open(MEMORY_MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Split on § or double newlines
    entries = [e.strip() for e in content.split("§") if e.strip()]
    if not entries:
        entries = [e.strip() for e in content.split("\n\n") if e.strip()]

    print(f"Found {len(entries)} entries in {MEMORY_MD_PATH}. Ingesting into Mem0...")
    count = 0
    for entry in entries:
        res = add_memory(entry, user_id=user_id, category="hermes_durable", source="MEMORY.md")
        if res.get("status") == "ok":
            count += 1

    print(f"Successfully ingested {count}/{len(entries)} memories into Mem0.")
    return count


def main():
    parser = argparse.ArgumentParser(description="aios-memory: Battle-tested Mem0 memory CLI for AI-OS")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    add_p = subparsers.add_parser("add", help="Store a memory / fact into Mem0")
    add_p.add_argument("text", help="Memory text content")
    add_p.add_argument("--user-id", default=DEFAULT_USER_ID, help="User identifier")
    add_p.add_argument("--category", default="general", help="Category tag")
    add_p.add_argument("--source", default="ai-os", help="Source provenance")

    # search
    search_p = subparsers.add_parser("search", help="Semantic search for memories")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--user-id", default=DEFAULT_USER_ID, help="User identifier")
    search_p.add_argument("--limit", type=int, default=5, help="Max results")

    # prefetch
    prefetch_p = subparsers.add_parser("prefetch", help="Format memories into markdown for context prefetch")
    prefetch_p.add_argument("query", help="Task or turn query")
    prefetch_p.add_argument("--user-id", default=DEFAULT_USER_ID, help="User identifier")
    prefetch_p.add_argument("--limit", type=int, default=5, help="Max results")

    # list
    list_p = subparsers.add_parser("list", help="List all stored memories")
    list_p.add_argument("--user-id", default=DEFAULT_USER_ID, help="User identifier")

    # delete
    del_p = subparsers.add_parser("delete", help="Delete a memory by ID")
    del_p.add_argument("memory_id", help="ID of memory to delete")

    # sync
    sync_p = subparsers.add_parser("sync", help="Ingest all entries from ~/.hermes/memories/MEMORY.md into Mem0")
    sync_p.add_argument("--user-id", default=DEFAULT_USER_ID, help="User identifier")

    args = parser.parse_args()

    if args.command == "add":
        result = add_memory(args.text, user_id=args.user_id, category=args.category, source=args.source)
        print(json.dumps(result, indent=2))

    elif args.command == "search":
        results = search_memories(args.query, user_id=args.user_id, limit=args.limit)
        print(json.dumps(results, indent=2))

    elif args.command == "prefetch":
        text = prefetch_context(args.query, user_id=args.user_id, limit=args.limit)
        if text:
            print(text)
        else:
            print("No relevant memories found.")

    elif args.command == "list":
        results = list_memories(user_id=args.user_id)
        print(json.dumps(results, indent=2))

    elif args.command == "delete":
        result = delete_memory(args.memory_id)
        print(json.dumps(result, indent=2))

    elif args.command == "sync":
        sync_from_hermes_memory_md(user_id=args.user_id)


if __name__ == "__main__":
    main()
