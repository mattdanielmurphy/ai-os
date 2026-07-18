#!/usr/bin/env python3
import os
import sys
import re
from pathlib import Path

# Add project root scripts directory to path to reuse skeletonization from ingest_codebase
scripts_dir = Path(__file__).resolve().parent
sys.path.append(str(scripts_dir))

from importlib.machinery import SourceFileLoader
try:
    ingest_codebase = SourceFileLoader("ingest_codebase", str(scripts_dir / "ingest_codebase")).load_module()
except Exception as e:
    print(f"Warning: Failed to import ingest_codebase: {e}", file=sys.stderr)
    ingest_codebase = None

EXCLUDE_DIRS = {
    "node_modules", ".git", "dist", "target", "tmp", "agent-logs", 
    "build", "__pycache__", ".vscode", ".idea", ".tauri", "out",
    "gemini-history", ".gemini", "tauri-gui/node_modules"
}

CODE_EXTENSIONS = {".py", ".ts", ".js", ".tsx", ".jsx", ".rs", ".go"}

def extract_signatures_js_ts(content):
    """Extract structural signatures (imports, classes, interfaces, types, functions, methods) from JS/TS."""
    lines = content.splitlines()
    output_lines = []
    
    # Matches class, interface, type, enum, function declarations
    decl_pattern = re.compile(
        r'^\s*(export\s+)?(default\s+)?(class|interface|type|enum|function|async\s+function|const\s+\w+\s*=\s*(\([^)]*\)|_?\w+)\s*=>)\b'
    )
    # Matches method signatures inside classes (e.g. constructor, async foo(), public bar())
    method_pattern = re.compile(
        r'^\s*(public|private|protected|readonly|static|async|get|set)?\s*\w+\s*\([^)]*\)\s*({|:|\w)'
    )
    # Matches imports
    import_pattern = re.compile(r'^\s*(import\s|export\s+.*\s+from\s)')
    
    in_multiline_comment = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # Handle multiline comments
        if in_multiline_comment:
            if "*/" in stripped:
                in_multiline_comment = False
            continue
        if stripped.startswith("/*"):
            if "*/" not in stripped:
                in_multiline_comment = True
            continue
        if stripped.startswith("//"):
            continue
            
        # Match declarations, imports, or methods
        if import_pattern.match(line) or decl_pattern.match(line) or method_pattern.match(line):
            # Clean up implementation braces on same line
            line_clean = re.sub(r'\s*\{.*$', ' { ... }', line)
            output_lines.append(line_clean)
            
    return "\n".join(output_lines)

def extract_signatures_rust(content):
    """Extract structural signatures (use, pub, fn, struct, enum, impl, trait) from Rust."""
    lines = content.splitlines()
    output_lines = []
    
    rust_pattern = re.compile(
        r'^\s*(pub\s+)?(fn|struct|enum|impl|trait|const|static|type|use)\b'
    )
    
    in_multiline_comment = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        if in_multiline_comment:
            if "*/" in stripped:
                in_multiline_comment = False
            continue
        if stripped.startswith("/*"):
            if "*/" not in stripped:
                in_multiline_comment = True
            continue
        if stripped.startswith("//"):
            continue
            
        if rust_pattern.match(line):
            line_clean = re.sub(r'\s*\{.*$', ' { ... }', line)
            output_lines.append(line_clean)
            
    return "\n".join(output_lines)

def extract_signatures_go(content):
    """Extract structural signatures (package, import, type, func) from Go."""
    lines = content.splitlines()
    output_lines = []
    
    go_pattern = re.compile(
        r'^\s*(package|import|type|func)\b'
    )
    
    in_multiline_comment = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        if in_multiline_comment:
            if "*/" in stripped:
                in_multiline_comment = False
            continue
        if stripped.startswith("/*"):
            if "*/" not in stripped:
                in_multiline_comment = True
            continue
        if stripped.startswith("//"):
            continue
            
        if go_pattern.match(line):
            line_clean = re.sub(r'\s*\{.*$', ' { ... }', line)
            output_lines.append(line_clean)
            
    return "\n".join(output_lines)

def process_file_repo_map(file_path):
    path = Path(file_path)
    ext = path.suffix.lower()
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if ext == ".py" and ingest_codebase:
            return ingest_codebase.skeletonize_python(content)
        elif ext in (".ts", ".js", ".tsx", ".jsx"):
            return extract_signatures_js_ts(content)
        elif ext == ".rs":
            return extract_signatures_rust(content)
        elif ext == ".go":
            return extract_signatures_go(content)
        else:
            if ingest_codebase:
                return ingest_codebase.process_file(str(path))
            return "[Parsing unavailable]"
    except Exception as e:
        return f"[Error: {e}]"

def generate_map(workspace_path):
    workspace = Path(workspace_path).resolve()
    if not workspace.exists():
        return f"Error: Workspace path {workspace_path} does not exist."

    outputs = []
    
    # Walk the directory tree
    for root, dirs, files in os.walk(workspace):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        
        for file in sorted(files):
            file_path = Path(root) / file
            ext = file_path.suffix.lower()
            
            if ext not in CODE_EXTENSIONS:
                continue
                
            rel_path = file_path.relative_to(workspace)
            
            outputs.append(f"\n# File: {rel_path}\n")
            
            skeleton = process_file_repo_map(file_path)
            indented = "\n".join(f"  {line}" for line in skeleton.splitlines())
            outputs.append(indented + "\n")
                
    return "".join(outputs)

def main():
    workspace = os.getcwd()
    if len(sys.argv) > 1:
        workspace = sys.argv[1]
        
    output_dir = Path(workspace) / ".devtool"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "repo_map.txt"
    
    print(f"Generating repo map for {workspace}...")
    repo_map_content = generate_map(workspace)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(repo_map_content)
        
    print(f"Repo map written to {output_file}")

if __name__ == "__main__":
    main()
