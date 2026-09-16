#!/usr/bin/env python3
import os
import sys
import argparse
import re
import datetime
from collections import defaultdict

def parse_frontmatter(content):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}
    
    yaml_text = match.group(1)
    data = {}
    current_key = None
    list_items = []
    
    for line in yaml_text.splitlines():
        # Handle list items
        if line.strip().startswith("-"):
            val = line.strip().lstrip("-").strip()
            # Extract wikilink if present e.g. [[Habit]] -> Habit
            wikilink_match = re.match(r"^\[\[(.*?)\]\]$", val)
            if wikilink_match:
                val = wikilink_match.group(1)
            list_items.append(val)
            if current_key:
                data[current_key] = list_items
            continue
        
        # Handle key-value
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip()
            # Clean string quotes
            val = val.strip("\"'")
            
            # Reset lists if a new key is found
            current_key = key
            list_items = []
            
            # Parse simple values
            if val:
                # check if inline list
                inline_list_match = re.match(r"^\[(.*?)\]$", val)
                if inline_list_match:
                    items = [i.strip().strip("\"'") for i in inline_list_match.group(1).split(",")]
                    # resolve wikilinks in inline list
                    resolved_items = []
                    for it in items:
                        wm = re.match(r"^\[\[(.*?)\]\]$", it)
                        resolved_items.append(wm.group(1) if wm else it)
                    data[key] = resolved_items
                else:
                    data[key] = val
            else:
                data[key] = []
                
    return data

def scan_logs(logs_dir):
    completions = defaultdict(set) # habit -> set of date strings (YYYY-MM-DD)
    if not os.path.isdir(logs_dir):
        return completions

    for filename in os.listdir(logs_dir):
        if not filename.endswith(".md"):
            continue
        # Extract date from filename YYYY-MM-DD.md
        date_match = re.match(r"^(\d{4}-\d{2}-\d{2})\.md$", filename)
        if not date_match:
            continue
        date_str = date_match.group(1)
        filepath = os.path.join(logs_dir, filename)
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            metadata = parse_frontmatter(content)
            completed_list = metadata.get("completed", [])
            for habit in completed_list:
                completions[habit].add(date_str)
        except Exception as e:
            print(f"Error parsing {filename}: {e}", file=sys.stderr)
            
    return completions

def generate_svg_heatmap(habit_name, completed_dates, days_to_show=365):
    # Determine the date range
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days_to_show)
    
    # Align to the start of that week (Sunday=0, Saturday=6)
    # in python weekday() returns 0 for Monday, 6 for Sunday
    # Let's adjust start_date so it falls on Sunday
    start_weekday = (start_date.weekday() + 1) % 7
    if start_weekday != 0:
        start_date = start_date - datetime.timedelta(days=start_weekday)
        
    # Calculate grid layout
    rect_size = 11
    gap = 2
    header_height = 20
    sidebar_width = 30
    
    num_weeks = (today - start_date).days // 7 + 1
    width = sidebar_width + num_weeks * (rect_size + gap) + 10
    height = header_height + 7 * (rect_size + gap) + 15
    
    svg = []
    svg.append(f'<svg viewBox="0 0 {width} {height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">')
    # Style
    svg.append("""  <style>
    .meta-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 9px; fill: #888888; }
    .title-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 11px; font-weight: 600; fill: #333333; }
    .day-rect { rx: 2px; ry: 2px; }
  </style>""")
    
    # Background / Title
    svg.append(f'  <text x="{sidebar_width}" y="12" class="title-text">{habit_name} Completion Heatmap</text>')
    
    # Weekday labels
    days_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for i, label in enumerate(days_labels):
        if i % 2 == 1: # Mon, Wed, Fri
            y_pos = header_height + i * (rect_size + gap) + 9
            svg.append(f'  <text x="5" y="{y_pos}" class="meta-text">{label}</text>')
            
    # Draw contribution grid
    current_date = start_date
    col = 0
    
    while current_date <= today:
        # Weekday index (0=Sunday, 6=Saturday)
        wday = (current_date.weekday() + 1) % 7
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Color intensity
        is_completed = date_str in completed_dates
        fill_color = "#ebedf0" # Default empty
        if is_completed:
            fill_color = "#39d353" # Completed green
            
        x_pos = sidebar_width + col * (rect_size + gap)
        y_pos = header_height + wday * (rect_size + gap)
        
        svg.append(f'  <rect x="{x_pos}" y="{y_pos}" width="{rect_size}" height="{rect_size}" class="day-rect" fill="{fill_color}">')
        svg.append(f'    <title>{date_str}: {"Completed" if is_completed else "Not Completed"}</title>')
        svg.append('  </rect>')
        
        # If Saturday, move to next column
        if wday == 6:
            col += 1
            
        current_date += datetime.timedelta(days=1)
        
    svg.append('</svg>')
    return "\n".join(svg)

def main():
    parser = argparse.ArgumentParser(description="Zero-Database Markdown Habit Tracker")
    parser.add_argument("--logs-dir", default="/Users/matt/projects/ai-os/habits/logs", help="Path to habits logs directory")
    parser.add_argument("--habit", help="Specific habit to generate heatmap for")
    parser.add_argument("--output", help="Path to save the generated SVG file")
    
    args = parser.parse_args()
    
    # Parse completions
    completions = scan_logs(args.logs_dir)
    
    if not completions:
        print("No completions found. Please check logs directory or log files format.")
        sys.exit(0)
        
    # Select habit
    habit_name = args.habit
    if not habit_name:
        # Default to the most active habit
        habits_sorted = sorted(completions.items(), key=lambda x: len(x[1]), reverse=True)
        habit_name = habits_sorted[0][0]
        print(f"No habit specified. Defaulting to most active: '{habit_name}'")
        
    dates = completions[habit_name]
    print(f"Found {len(dates)} completions for '{habit_name}'")
    
    svg_content = generate_svg_heatmap(habit_name, dates)
    
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Saved heatmap SVG to {args.output}")
    else:
        # Print SVG to stdout
        print(svg_content)

if __name__ == "__main__":
    main()
