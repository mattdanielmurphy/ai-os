#!/usr/bin/env python3
"""
sanitize_thread.py — High-Performance Secret and Credential Sanitizer for ai-os

Scrubs credentials, active API keys, bearer tokens, and .env key-value pairs
from conversation markdown threads, logs, and git-staged changes.
"""

import os
import sys
import re
import glob
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

@dataclass
class SanitizationResult:
    cleaned_text: str
    secrets_found_count: int
    detected_types: Set[str] = field(default_factory=set)
    audit_trail: List[Dict[str, str]] = field(default_factory=list)

class SecretSanitizer:
    """High-performance text sanitizer with in-memory exact matching and regex filtering."""

    DEFAULT_REGEX_PATTERNS = [
        ("OPENAI_KEY", re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b'), "[REDACTED_OPENAI_KEY]"),
        ("GOOGLE_KEY", re.compile(r'\bAIza[0-9A-Za-z-_]{35}\b'), "[REDACTED_GOOGLE_API_KEY]"),
        ("GITHUB_TOKEN", re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{60,})\b'), "[REDACTED_GITHUB_TOKEN]"),
        ("ANTHROPIC_KEY", re.compile(r'\bsk-ant-[A-Za-z0-9_-]{30,}\b'), "[REDACTED_ANTHROPIC_KEY]"),
        ("AWS_ACCESS_KEY", re.compile(r'\bAKIA[0-9A-Z]{16}\b'), "[REDACTED_AWS_KEY]"),
        ("SLACK_TOKEN", re.compile(r'\bxox[baprs]-[0-9A-Za-z-]{20,}\b'), "[REDACTED_SLACK_TOKEN]"),
        ("BEARER_AUTH", re.compile(r'(?i)\bBearer\s+([A-Za-z0-9_\-\.]{25,})\b'), "Bearer [REDACTED_BEARER_TOKEN]"),
        ("PRIVATE_KEY", re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----'), "[REDACTED_PRIVATE_KEY_BLOCK]"),
        ("DATABASE_AUTH_URI", re.compile(r'(?i)(postgres|mysql|mongodb(?:\+srv)?|redis)://([^:]+):([^@\s]+)@'), r"\1://\2:[REDACTED_PASSWORD]@"),
    ]

    def __init__(self, extra_env_dirs: Optional[List[Path]] = None):
        self.exact_match_dict: Dict[str, str] = {}
        self.regex_patterns = list(self.DEFAULT_REGEX_PATTERNS)
        self._load_all_known_secrets(extra_env_dirs)

    def _load_all_known_secrets(self, extra_dirs: Optional[List[Path]] = None):
        """Scans local project and config roots for active .env files to register known secrets in memory."""
        search_dirs = [
            Path("/Users/matt/projects/ai-os"),
            Path("/Users/matt/.gemini"),
            Path("/Users/matt/.hermes"),
            Path.cwd(),
        ]
        if extra_dirs:
            search_dirs.extend(extra_dirs)

        seen_files = set()
        for s_dir in search_dirs:
            if not s_dir.exists():
                continue
            for env_candidate in s_dir.glob("**/.env*"):
                if env_candidate.is_file() and env_candidate not in seen_files:
                    seen_files.add(env_candidate)
                    self.register_env_file(env_candidate)

    def register_env_file(self, env_file_path: Path):
        """Loads secret values from an env file in-memory for exact string replacement."""
        try:
            with open(env_file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    # Only register secret-like values with sufficient entropy (length >= 8)
                    if len(val) >= 8 and not val.lower() in ("true", "false", "development", "production", "127.0.0.1", "localhost"):
                        self.exact_match_dict[val] = f"[REDACTED_SECRET:{key}]"
        except Exception:
            pass

    def sanitize_content(self, text: str) -> SanitizationResult:
        """Applies exact-match redaction and heuristic regex filtering across text."""
        if not text:
            return SanitizationResult(cleaned_text="", secrets_found_count=0)

        cleaned = text
        secrets_count = 0
        detected_types: Set[str] = set()
        audit_trail = []

        # 1. Exact-match in-memory redaction (longest strings first)
        for secret_val, replacement in sorted(self.exact_match_dict.items(), key=lambda x: len(x[0]), reverse=True):
            if secret_val in cleaned:
                count = cleaned.count(secret_val)
                secrets_count += count
                detected_types.add("EXACT_ENV_MATCH")
                audit_trail.append({"type": "EXACT_MATCH", "replacement": replacement, "occurrences": count})
                cleaned = cleaned.replace(secret_val, replacement)

        # 2. Regex heuristic patterns
        for name, pattern, replacement in self.regex_patterns:
            matches = list(pattern.finditer(cleaned))
            if matches:
                secrets_count += len(matches)
                detected_types.add(name)
                audit_trail.append({"type": name, "replacement": str(replacement), "occurrences": len(matches)})
                cleaned = pattern.sub(replacement, cleaned)

        return SanitizationResult(
            cleaned_text=cleaned,
            secrets_found_count=secrets_count,
            detected_types=detected_types,
            audit_trail=audit_trail
        )

    def sanitize_file(self, input_path: Path, output_path: Optional[Path] = None) -> SanitizationResult:
        """Reads a file, scrubs sensitive tokens, and writes the sanitized output."""
        target_output = output_path or input_path
        if not input_path.exists():
            return SanitizationResult(cleaned_text="", secrets_found_count=0)

        try:
            content = input_path.read_text(encoding="utf-8", errors="ignore")
            res = self.sanitize_content(content)
            if res.secrets_found_count > 0 or target_output != input_path:
                target_output.parent.mkdir(parents=True, exist_ok=True)
                target_output.write_text(res.cleaned_text, encoding="utf-8")
            return res
        except Exception as e:
            print(f"Error sanitizing file {input_path}: {e}", file=sys.stderr)
            return SanitizationResult(cleaned_text="", secrets_found_count=0)


class SecretAuditHook:
    """Preflight and pre-commit secret audit gate."""

    @staticmethod
    def audit_git_diff(repo_root: Optional[Path] = None) -> Tuple[bool, List[str]]:
        """Scans staged and working tree git diffs for raw secrets or .env additions."""
        import subprocess
        root = repo_root or Path.cwd()
        
        errors = []
        sanitizer = SecretSanitizer()

        # Check for staged .env files
        staged_files_proc = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=str(root)
        )
        if staged_files_proc.returncode == 0:
            for fname in staged_files_proc.stdout.splitlines():
                if re.search(r'(?:^|/)(\.env(?:\.[a-zA-Z0-9_\-]+)*)$', fname, re.IGNORECASE):
                    errors.append(f"STAGED_ENV_FILE: Attempted to stage environment file '{fname}'. Remove with 'git reset HEAD {fname}'.")

        # Check staged diff content
        staged_diff_proc = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, cwd=str(root)
        )
        if staged_diff_proc.returncode == 0 and staged_diff_proc.stdout:
            added_lines = [line[1:] for line in staged_diff_proc.stdout.splitlines() if line.startswith("+") and not line.startswith("+++")]
            diff_text = "\n".join(added_lines)
            res = sanitizer.sanitize_content(diff_text)
            if res.secrets_found_count > 0:
                errors.append(f"STAGED_SECRET_LEAK: Detected {res.secrets_found_count} raw secret(s) in staged diff: {', '.join(res.detected_types)}")

        return (len(errors) == 0, errors)


def main():
    parser = argparse.ArgumentParser(description="SecretSanitizer: Sanitize conversation threads and audit git diffs")
    parser.add_argument("path", nargs="?", help="File or directory path to sanitize")
    parser.add_argument("--audit-git", action="store_true", help="Audit git staged diffs for raw secrets")
    parser.add_argument("--output", "-o", help="Output file path (default: overwrite input)")
    args = parser.parse_args()

    if args.audit_git:
        is_clean, errors = SecretAuditHook.audit_git_diff()
        if not is_clean:
            print("❌ PRE-COMMIT SECRET AUDIT FAILED:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            sys.exit(1)
        else:
            print("✅ Secret Audit: Clean (no staged secrets or .env files detected)")
            sys.exit(0)

    if not args.path:
        parser.print_help()
        sys.exit(1)

    target = Path(args.path).resolve()
    sanitizer = SecretSanitizer()

    if target.is_file():
        out_p = Path(args.output).resolve() if args.output else target
        res = sanitizer.sanitize_file(target, out_p)
        print(f"Sanitized '{target}': {res.secrets_found_count} secrets redacted ({', '.join(res.detected_types) or 'Clean'})")
    elif target.is_dir():
        count = 0
        redacted_total = 0
        for md_file in target.glob("**/*.md"):
            res = sanitizer.sanitize_file(md_file)
            if res.secrets_found_count > 0:
                count += 1
                redacted_total += res.secrets_found_count
                print(f"Redacted {res.secrets_found_count} secrets in '{md_file.name}'")
        print(f"Sanitization complete: {redacted_total} secrets redacted across {count} files in {target}")


if __name__ == "__main__":
    main()
