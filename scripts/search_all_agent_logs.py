#!/usr/bin/env python3
import argparse
import subprocess
import os

def search_agent_logs(query, projects_root="~/projects"):
    projects_root = os.path.expanduser(projects_root)
    found_matches = False
    results = []

    if not os.path.exists(projects_root):
        print(f"Error: Projects root directory '{projects_root}' does not exist.")
        return

    for project_dir in os.listdir(projects_root):
        project_path = os.path.join(projects_root, project_dir)
        if not os.path.isdir(project_path):
            continue

        agent_log_patterns = [
            os.path.join(project_path, "agent-logs"),
            os.path.join(project_path, ".agent-logs")
        ]

        for log_pattern in agent_log_patterns:
            if os.path.isdir(log_pattern):
                try:
                    # Use ripgrep to search for the query in .md files within the agent log directory
                    cmd = [
                        "rg",
                        "--color", "always",
                        "--with-filename",
                        "--line-number",
                        "--ignore-case",
                        "--glob", "*.md",
                        query,
                        log_pattern
                    ]

                    process = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    if process.stdout:
                        results.append(f"### Results in `{log_pattern}`:\n```ansi\n{process.stdout.strip()}\n```")
                        found_matches = True
                except subprocess.CalledProcessError as e:
                    # ripgrep returns a non-zero exit code if no matches are found
                    if e.returncode == 1:
                        continue
                    else:
                        results.append(f"### Error searching in `{log_pattern}`:\n```\n{e.stderr.strip()}\n```")
                        found_matches = True
                except FileNotFoundError:
                    print("Error: ripgrep (rg) not found. Please install it to use this script (e.g., `brew install ripgrep`).")
                    return

    if found_matches:
        print("# Agent Log Search Results\n")
        print("\n".join(results))
    else:
        print(f"No matches found for '{query}' in any agent log files within '{projects_root}' and its subdirectories.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for a query in agent log files across sandboxed project folders.")
    parser.add_argument("query", help="The search query.")
    parser.add_argument("--projects-root", default="~/projects",
                        help="The root directory containing sandboxed project folders (default: ~/projects).")
    args = parser.parse_args()

    search_agent_logs(args.query, args.projects_root)
