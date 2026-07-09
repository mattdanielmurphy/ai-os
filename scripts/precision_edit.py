import argparse

def precision_edit(
    filepath: str,
    command: str,
    target_text: str = "",
    replacement_text: str = "",
    start_line: int = 0,
    end_line: int = 0,
):
    """
    Performs precise text replacements, appends, or inserts into a file.

    Args:
        filepath (str): Path to the target file.
        command (str): Action to perform: "replace", "append", or "insert_after_string".
        target_text (str): The text portion to target for replacement or insertion. Required for "replace" and "insert_after_string".
        replacement_text (str): The text to insert or replace with. Required for "replace", "append", and "insert_after_string".
        start_line (int, optional): 1-based starting line number for the operation. Defaults to 0 (beginning of file).
        end_line (int, optional): 1-based ending line number for the operation. Defaults to 0 (end of file).
    """
    with open(filepath, "r") as f:
        lines = f.readlines()

    original_content = "".join(lines)
    new_content = []
    modified = False

    # Adjust line numbers to be 0-based for list indexing
    start_idx = start_line - 1 if start_line > 0 else 0
    end_idx = end_line if end_line > 0 else len(lines)

    if start_idx < 0 or start_idx >= len(lines):
        print(f"Error: start_line {start_line} is out of bounds.")
        return
    if end_idx < 0 or end_idx > len(lines):
        print(f"Error: end_line {end_line} is out of bounds.")
        return
    if start_idx > end_idx:
        print(f"Error: start_line {start_line} cannot be after end_line {end_line}.")
        return

    processed_lines = lines[start_idx:end_idx]
    remainder_before = lines[:start_idx]
    remainder_after = lines[end_idx:]

    if command == "replace":
        if not target_text:
            print("Error: target_text is required for 'replace' command.")
            return
        temp_content = "".join(processed_lines)
        if target_text in temp_content:
            temp_content = temp_content.replace(target_text, replacement_text)
            new_content = remainder_before + temp_content.splitlines(keepends=True) + remainder_after
            modified = True
        else:
            print(f"'{target_text}' not found in the specified range.")
            return
    elif command == "append":
        temp_content = "".join(processed_lines)
        temp_content += replacement_text
        new_content = remainder_before + temp_content.splitlines(keepends=True) + remainder_after
        modified = True
    elif command == "insert_after_string":
        if not target_text:
            print("Error: target_text is required for 'insert_after_string' command.")
            return
        temp_content = "".join(processed_lines)
        if target_text in temp_content:
            temp_content = temp_content.replace(target_text, target_text + replacement_text, 1)
            new_content = remainder_before + temp_content.splitlines(keepends=True) + remainder_after
            modified = True
        else:
            print(f"'{target_text}' not found in the specified range.")
            return
    else:
        print(f"Error: Unknown command ' {command} '. Supported commands are 'replace', 'append', 'insert_after_string'.")
        return

    if modified:
        with open(filepath, "w") as f:
            f.writelines(new_content)
        print(f"File '{filepath}' modified successfully.")
    else:
        print("No changes made to the file.")


def main():
    parser = argparse.ArgumentParser(description="Perform precise text edits on a file.")
    parser.add_argument("filepath", help="Path to the target file.")
    parser.add_argument("command", choices=["replace", "append", "insert_after_string"], help="Action to perform.")
    parser.add_argument("--target_text", default="", help="The text portion to target for replacement or insertion. Required for 'replace' and 'insert_after_string'.")
    parser.add_argument("--replacement_text", default="", help="The text to insert or replace with. Required for 'replace', 'append', and 'insert_after_string'.")
    parser.add_argument("--start_line", type=int, default=0, help="1-based starting line number for the operation. Defaults to 0 (beginning of file).")
    parser.add_argument("--end_line", type=int, default=0, help="1-based ending line number for the operation. Defaults to 0 (end of file).")

    args = parser.parse_args()

    precision_edit(
        filepath=args.filepath,
        command=args.command,
        target_text=args.target_text,
        replacement_text=args.replacement_text,
        start_line=args.start_line,
        end_line=args.end_line,
    )


if __name__ == "__main__":
    main()
