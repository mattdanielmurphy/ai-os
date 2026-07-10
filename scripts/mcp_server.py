import sys
import json
import subprocess
import os

# Helper to send JSON RPC responses
def send_response(response):
    json_response = json.dumps(response)
    sys.stdout.write(json_response + "\n")
    sys.stdout.flush()

def send_error(id, code, message, data=None):
    error_response = {
        "jsonrpc": "2.0",
        "id": id,
        "error": {
            "code": code,
            "message": message
        }
    }
    if data is not None:
        error_response["error"]["data"] = data
    send_response(error_response)

def handle_request(request):
    method = request.get("method")
    params = request.get("params")
    id = request.get("id")

    if method == "initialize":
        response = {
            "jsonrpc": "2.0",
            "id": id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "MCP Python Server",
                    "version": "1.0"
                },
                "capabilities": {
                    "tools": {
                        "search_all_agent_logs": {
                            "description": "Searches for agent logs with a given query.",
                            "arguments": {
                                "query": {
                                    "type": "string",
                                    "description": "The query string to search for."
                                }
                            }
                        },
                        "delegate_research": {
                            "description": "Delegates a research query to a sub-agent for summarization.",
                            "arguments": {
                                "query": {
                                    "type": "string",
                                    "description": "The query string for research."
                                }
                            }
                        },
                        "read_lines": {
                            "description": "Reads a specific line range from a file to save context tokens.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "file_path": {"type": "string", "description": "The absolute path to the file to read."},
                                    "start_line": {"type": "integer", "description": "The 1-based start line (inclusive). Default is 1."},
                                    "end_line": {"type": "integer", "description": "The 1-based end line (inclusive). Default is start_line + 50."}
                                },
                                "required": ["file_path"]
                            }
                        }
                    }
                }
            }
        }
        send_response(response)
    elif method == "tools/list":
        response = {
            "jsonrpc": "2.0",
            "id": id,
            "result": {
                "tools": {
                    "search_all_agent_logs": {
                        "description": "Searches for agent logs with a given query.",
                        "arguments": {
                            "query": {
                                "type": "string",
                                "description": "The query string to search for."
                            }
                        }
                    },
                    "delegate_research": {
                        "description": "Delegates a research query to a sub-agent for summarization.",
                        "arguments": {
                            "query": {
                                "type": "string",
                                "description": "The query string for research."
                            }
                        }
                    }
                }
            }
        }
        send_response(response)
    elif method == "tools/call":
        tool_name = params.get("tool")
        tool_args = params.get("arguments", {})
        query = tool_args.get("query")

        if tool_name == "search_all_agent_logs":
            script_path = os.path.join(os.path.dirname(__file__), "search_all_agent_logs.py")
            if not os.path.exists(script_path):
                send_error(id, -32601, f"Script not found: {script_path}")
                return
            try:
                result = subprocess.run([sys.executable, script_path, query], capture_output=True, text=True, check=True)
                send_response({
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {
                        "content": result.stdout
                    }
                })
            except subprocess.CalledProcessError as e:
                send_error(id, 1, f"Error running search_all_agent_logs: {e.stderr}", data=str(e))
            except Exception as e:
                send_error(id, -32000, f"Unexpected error: {str(e)}")

        elif tool_name == "delegate_research":
            script_path = os.path.join(os.path.dirname(__file__), "research_agent.py")
            if not os.path.exists(script_path):
                send_error(id, -32601, f"Script not found: {script_path}")
                return
            try:
                result = subprocess.run([sys.executable, script_path, query], capture_output=True, text=True, check=True)
                send_response({
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {
                        "content": result.stdout
                    }
                })
            except subprocess.CalledProcessError as e:
                send_error(id, 1, f"Error running research_agent: {e.stderr}", data=str(e))
            except Exception as e:
                send_error(id, -32000, f"Unexpected error: {str(e)}")

        elif tool_name == 'read_lines':
            file_path = tool_args.get('file_path')
            start = tool_args.get('start_line', 1)
            end = tool_args.get('end_line', start + 50)

            if not os.path.exists(file_path):
                send_error(id, -32602, f'File not found: {file_path}')
                return

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    chunk = ''.join(f'{i+1}: {line}' for i, line in enumerate(lines) if start <= i+1 <= end)
                send_response({'jsonrpc': '2.0', 'id': id, 'result': {'content': [{'type': 'text', 'text': chunk}]}})
            except Exception as e:
                send_error(id, -32000, f'Error reading file: {str(e)}')

        else:
            send_error(id, -32601, f"Method not found: {tool_name}")
    elif method == "notifications/initialized":
        # No-op for initialized notification
        pass
    else:
        send_error(id, -32601, f"Method not found: {method}")

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            request = json.loads(line)
            handle_request(request)
        except json.JSONDecodeError:
            send_error(None, -32700, "Parse error")
        except Exception as e:
            send_error(None, -32000, f"Internal error: {str(e)}")


if __name__ == "__main__":
    main()
