import argparse
import subprocess
import json
import os

def main():
    parser = argparse.ArgumentParser(description="Research agent that queries workspace and summarizes content.")
    parser.add_argument("query", help="The query string for research.")

    args = parser.parse_args()

    # Step 1: Run ripgrep (rg) in the workspace
    rg_command = [
        "rg",
        "-i",
        "-n",
        "-C", "2",
        "--max-columns", "300",
        args.query,
        "."  # Search in the current workspace
    ]

    try:
        rg_result = subprocess.run(rg_command, capture_output=True, text=True, check=False)
        # rg returns 1 if no matches are found, so we don't use check=True here
        search_results = rg_result.stdout
        if rg_result.returncode != 0 and rg_result.returncode != 1:
            print(f"Error during ripgrep search: {rg_result.stderr}")
            return
    except FileNotFoundError:
        print("Error: ripgrep (rg) command not found. Please install ripgrep to use this script.")
        return

    if not search_results:
        summary = f"No relevant information found in the workspace for query: '{args.query}'."
        print(summary)
        return

    # Step 2: Pass search results to LiteLLM proxy for summarization
    litellm_url = "http://localhost:8082/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "claude-haiku*",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful research assistant. Condense the provided search results into a succinct markdown summary, highlighting file paths, relevant code signatures, and logical blocks that match the user's query."
            },
            {
                "role": "user",
                "content": f"Search Query: '{args.query}'\n\nSearch Results:\n```\n{search_results}\n```\n\nPlease provide a succinct markdown summary."
            }
        ]
    }

    try:
        # Using subprocess to call curl as requests library might not be available or requires installation
        curl_command = [
            "curl",
            "-s",
            "-X", "POST",
            "-H", "Content-Type: application/json",
            "--data", json.dumps(payload),
            litellm_url
        ]

        litellm_response = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        response_json = json.loads(litellm_response.stdout)

        summary = response_json["choices"][0]["message"]["content"]
        print(summary)

    except subprocess.CalledProcessError as e:
        print(f"Error calling LiteLLM proxy with curl: {e}")
        print(f"Stderr: {e.stderr}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON response from LiteLLM proxy: {litellm_response.stdout}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
