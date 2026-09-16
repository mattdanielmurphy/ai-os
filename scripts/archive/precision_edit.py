
import argparse

def main():
    parser = argparse.ArgumentParser(description="Programmatically handles micro-edits in files.")
    parser.add_argument("file", help="The file to edit.")
    parser.add_argument("action", choices=["replace", "append", "insert_after"], help="The action to perform.")
    parser.add_argument("--target", help="The target string for replace and insert_after actions.")
    parser.add_argument("--content", required=True, help="The content to insert or replace with.")

    args = parser.parse_args()

    try:
        with open(args.file, 'r') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {args.file}")
        return

    new_data = ""
    if args.action == "replace":
        if not args.target:
            print("Error: --target is required for 'replace' action.")
            return
        new_data = data.replace(args.target, args.content)
    elif args.action == "append":
        new_data = data + args.content
    elif args.action == "insert_after":
        if not args.target:
            print("Error: --target is required for 'insert_after' action.")
            return
        new_data = data.replace(args.target, args.target + args.content)

    if new_data == data:
        print("No changes made. Target not found or content already present.")
        return

    with open(args.file, 'w') as f:
        f.write(new_data)
    print(f"File {args.file} successfully updated using action '{args.action}'.")

if __name__ == "__main__":
    main()
