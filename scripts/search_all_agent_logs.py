import argparse
import subprocess
import os

def main():
    parser = argparse.ArgumentParser(description="Searches for agent logs across the projects base.")
    parser.add_argument("query", help="The query string to search for.")

    args = parser.parse_args()

    home_dir = os.path.expanduser("~")
    search_path = os.path.join(home_dir, "projects/")

    # Ensure the path exists, otherwise `rg` might complain
    if not os.path.isdir(search_path):
        print(f"Search path does not exist: {search_path}")
        return

    rg_command = [
        "rg",
        "-i",
        "-n",
        "-C", "2",
        "--max-columns", "300",
        "--type-add", "agentlog:*/.agent-logs/*.md",
        "--type-add", "agentlog:*/agent-logs/*.md",
        "-t", "agentlog",
        args.query,
        search_path
    ]

    try:
        result = subprocess.run(rg_command, capture_output=True, text=True, check=True)
        if result.stdout:
            print(result.stdout)
        else:
            print(f"No matches found for '{args.query}' in agent logs.")
    except subprocess.CalledProcessError as e:
        # `rg` returns 1 if no matches are found, which is a CalledProcessError
        if e.returncode == 1:
            print(f"No matches found for '{args.query}' in agent logs.")
        else:
            print(f"An error occurred while running ripgrep: {e}")
            print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print("Error: ripgrep (rg) command not found. Please install ripgrep to use this script.")

if __name__ == "__main__":
    main()
