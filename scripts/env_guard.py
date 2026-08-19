#!/usr/bin/env python3
"""
env_guard.py — Safe Environment Variable Inspector and Command Validation Guard

Enforces the Zero-Secret Invariant:
1. Prevents agents from directly viewing, reading, or dumping raw .env contents.
2. Provides safe CLI tooling (`aios-env`) to check key existence, classification, length, and masked previews.
3. Provides command validation to intercept unsafe shell read operations targeting .env files.
"""

import os
import sys
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

class SecretClassification(Enum):
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    DATABASE_URI = "database_uri"
    PRIVATE_KEY = "private_key"
    GENERIC_SECRET = "generic_secret"
    CONFIG_PUBLIC = "config_public"

@dataclass(frozen=True)
class EnvMetadata:
    key: str
    is_set: bool
    length: int
    classification: SecretClassification
    file_path: str
    preview: str

class EnvGuard:
    """Interception hook and helper utility for environment variable inspection."""

    BLOCKED_PATTERNS = [
        re.compile(r'(?:^|/)(\.env(?:\.[a-zA-Z0-9_\-]+)*)$', re.IGNORECASE),
        re.compile(r'(?:^|/)(.*credentials(?:\.[a-zA-Z0-9_\-]+)*)$', re.IGNORECASE),
        re.compile(r'(?:^|/)(.*id_rsa|.*id_ed25519|.*\.pem|.*\.key)$', re.IGNORECASE),
    ]

    BLOCKED_COMMAND_REGEX = re.compile(
        r'\b(cat|head|tail|less|more|view|grep|egrep|fgrep|awk|sed|bat|rg|ag)\b[\s\S]*?(\.env(?:\.[a-zA-Z0-9_\-]+)*|\.env)',
        re.IGNORECASE
    )

    @classmethod
    def is_blocked_path(cls, path_str: str) -> bool:
        """Determines if the targeted path is a protected environment or credentials file."""
        if not path_str:
            return False
        clean_path = str(Path(path_str).resolve())
        basename = os.path.basename(clean_path)
        for pattern in cls.BLOCKED_PATTERNS:
            if pattern.search(basename) or pattern.search(clean_path):
                return True
        return False

    @classmethod
    def validate_command(cls, command: str) -> Tuple[bool, Optional[str]]:
        """Scans shell commands to block direct reads like cat .env or grep .env."""
        if not command:
            return True, None
        
        # Check direct regex match
        if cls.BLOCKED_COMMAND_REGEX.search(command):
            return False, f"Direct command read on .env file is forbidden. Use 'aios-env' instead of reading raw secrets."
        
        # Check python/node inline scripts trying to read .env directly
        if re.search(r'(?:open|readFile|readFileSync)\s*\(\s*[\'"].*?\.env[\'"]', command, re.IGNORECASE):
            return False, f"Inline script read of .env file is forbidden. Load environment into process memory safely."

        return True, None

    @classmethod
    def classify_key(cls, key: str, value: str) -> SecretClassification:
        key_upper = key.upper()
        if any(k in key_upper for k in ["KEY", "API", "TOKEN", "SECRET", "AUTH", "PASS"]):
            if "BEARER" in key_upper:
                return SecretClassification.BEARER_TOKEN
            elif "PRIVATE" in key_upper or "RSA" in key_upper:
                return SecretClassification.PRIVATE_KEY
            return SecretClassification.API_KEY
        elif any(k in key_upper for k in ["DB", "DATABASE", "POSTGRES", "MONGO", "REDIS", "URI", "URL"]):
            if "://" in value:
                return SecretClassification.DATABASE_URI
        elif len(value) > 20 and any(c.isdigit() for c in value) and any(c.isupper() for c in value):
            return SecretClassification.GENERIC_SECRET
        return SecretClassification.CONFIG_PUBLIC

    @classmethod
    def make_mask_preview(cls, val: str) -> str:
        if not val:
            return "(empty)"
        val_len = len(val)
        if val_len <= 6:
            return "*" * val_len
        elif val_len <= 12:
            return f"{val[:2]}...{val[-2:]}"
        else:
            return f"{val[:4]}...{val[-3:]} ({val_len} chars)"

    @classmethod
    def inspect_keys(cls, env_path: str = ".env") -> List[EnvMetadata]:
        """Parses .env without exposing raw values."""
        target_path = Path(env_path).resolve()
        if not target_path.exists():
            return []

        results = []
        try:
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    
                    classification = cls.classify_key(key, val)
                    preview = cls.make_mask_preview(val)
                    
                    results.append(EnvMetadata(
                        key=key,
                        is_set=bool(val),
                        length=len(val),
                        classification=classification,
                        file_path=str(target_path),
                        preview=preview
                    ))
        except Exception as e:
            print(f"Error inspecting {target_path}: {e}", file=sys.stderr)

        return results


def format_table(metadata_list: List[EnvMetadata]) -> str:
    if not metadata_list:
        return "No environment variables found."
    
    header = f"{'KEY NAME':<35} | {'SET?':<6} | {'LENGTH':<8} | {'CLASSIFICATION':<18} | {'PREVIEW'}"
    sep = "-" * len(header)
    rows = [header, sep]
    for meta in metadata_list:
        set_str = "YES" if meta.is_set else "NO"
        rows.append(f"{meta.key:<35} | {set_str:<6} | {meta.length:<8} | {meta.classification.value:<18} | {meta.preview}")
    return "\n".join(rows)


def main():
    parser = argparse.ArgumentParser(description="aios-env: Safe Environment Variable Inspection Tool")
    subparsers = parser.add_subparsers(dest="action", help="Subcommands")

    # list
    list_p = subparsers.add_parser("list", help="List environment keys and safe metadata without exposing values")
    list_p.add_argument("--env-path", "-e", default=".env", help="Path to .env file (default: .env)")

    # check
    check_p = subparsers.add_parser("check", help="Check specific key existence and metadata")
    check_p.add_argument("--key", "-k", required=True, help="Key name to inspect")
    check_p.add_argument("--env-path", "-e", default=".env", help="Path to .env file (default: .env)")

    # validate-command
    val_p = subparsers.add_parser("validate-command", help="Validate shell command for forbidden .env access")
    val_p.add_argument("command", help="Shell command string to validate")

    args = parser.parse_args()

    if args.action == "list":
        meta = EnvGuard.inspect_keys(args.env_path)
        print(format_table(meta))
    elif args.action == "check":
        meta_list = EnvGuard.inspect_keys(args.env_path)
        match = next((m for m in meta_list if m.key.upper() == args.key.upper()), None)
        if match:
            print(f"Key: {match.key}")
            print(f"Status: {'Configured (Set)' if match.is_set else 'Empty'}")
            print(f"Length: {match.length} chars")
            print(f"Classification: {match.classification.value}")
            print(f"Preview: {match.preview}")
            print(f"Source: {match.file_path}")
        else:
            print(f"Key '{args.key}' not found in {args.env_path}")
            sys.exit(1)
    elif args.action == "validate-command":
        is_safe, reason = EnvGuard.validate_command(args.command)
        if not is_safe:
            print(f"BLOCKED: {reason}", file=sys.stderr)
            sys.exit(1)
        else:
            print("SAFE")
    else:
        # Default action: list .env in cwd or project root
        meta = EnvGuard.inspect_keys(".env")
        if not meta:
            meta = EnvGuard.inspect_keys("/Users/matt/projects/ai-os/.env")
        print(format_table(meta))


if __name__ == "__main__":
    main()
