
import sqlite3
import plistlib
import os
import argparse

def export_text_replacements(db_path, output_path):
    # Resolve tilde paths
    db_path = os.path.expanduser(db_path)
    output_path = os.path.expanduser(output_path)

    # Check if the db file exists and is readable
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return
    if not os.access(db_path, os.R_OK):
        print(f"Error: Permission denied to read database file at {db_path}.")
        print("You might need to copy the database to a temporary location with appropriate permissions.")
        print(f"Suggested command: sudo cp {db_path} /tmp/LegacyTextReplacements.db && sudo chown $(whoami) /tmp/LegacyTextReplacements.db")
        print("Then run this script with --db /tmp/LegacyTextReplacements.db")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = "SELECT ZSHORTCUT, ZPHRASE FROM ZTEXTREPLACEMENTENTRY WHERE ZWASDELETED = 0 AND ZSHORTCUT IS NOT NULL AND ZPHRASE IS NOT NULL"
        cursor.execute(query)

        replacements = []
        for row in cursor.fetchall():
            replacements.append({"shortcut": row[0], "phrase": row[1]})

        with open(output_path, 'wb') as fp:
            plistlib.dump(replacements, fp)

        print(f"Successfully exported {len(replacements)} text replacements to {output_path}")
        print("To import, drag the generated .plist file into System Settings > Keyboard > Text Replacements.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export legacy macOS text replacements to a .plist file.")
    parser.add_argument("--db",
                        default="/Users/matthewmurphy/Library/KeyboardServices/TextReplacements.db",
                        help="Path to the TextReplacements.db file.")
    parser.add_argument("--output",
                        default="~/Desktop/LegacyTextReplacements.plist",
                        help="Output path for the .plist file.")
    args = parser.parse_args()

    export_text_replacements(args.db, args.output)
