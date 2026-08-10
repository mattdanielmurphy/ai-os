#!/usr/bin/env python3
import argparse
import random
import sys

def generate_brief():
    parser = argparse.ArgumentParser(description="Generate a harmonized UI design brief.")
    parser.add_argument('--surface', help='Surface commitment archetype')
    parser.add_argument('--theme', choices=['warm_paper', 'minimal_slate', 'cyber_ochre', 'emerald_studio', 'solarized', 'swiss'], help='Visual theme')
    
    args = parser.parse_args()

    # Data
    archetypes = ["Monitor", "Operate", "Compare", "Configure", "Decide/Learn", "Explore", "Command/Inspect"]
    themes = {
        'warm_paper': {
            'bg': '#fcfaf6', 'surface': '#f4f1ea', 'border': '#dcd9cf', 'text': '#3e3a34', 'accent': '#a66c39', 'accent_hover': '#8c5a2f'
        },
        'minimal_slate': {
            'bg': '#f8f9fa', 'surface': '#e9ecef', 'border': '#dee2e6', 'text': '#212529', 'accent': '#495057', 'accent_hover': '#343a40'
        },
        'cyber_ochre': {
            'bg': '#0a0a0a', 'surface': '#1a1a1a', 'border': '#333333', 'text': '#e0e0e0', 'accent': '#cc8800', 'accent_hover': '#aa7200'
        },
        'emerald_studio': {
            'bg': '#0a1a15', 'surface': '#152b24', 'border': '#254a40', 'text': '#d1e7dd', 'accent': '#20c997', 'accent_hover': '#1aa87d'
        },
        'solarized': {
            'bg': '#fdf6e3', 'surface': '#eee8d5', 'border': '#d3d3d3', 'text': '#586e75', 'accent': '#268bd2', 'accent_hover': '#2072a8'
        },
        'swiss': {
            'bg': '#ffffff', 'surface': '#f0f0f0', 'border': '#000000', 'text': '#000000', 'accent': '#ff0000', 'accent_hover': '#cc0000'
        }
    }
    typography = [
        ("Space Grotesk", "JetBrains Mono"),
        ("Inter", "Roboto Mono"),
        ("Geist", "Geist Mono"),
        ("Source Serif 4", "Source Sans 3"),
        ("IBM Plex Serif", "IBM Plex Mono")
    ]

    # Selection
    archetype = args.surface or random.choice(archetypes)
    theme_key = args.theme or random.choice(list(themes.keys()))
    palette = themes[theme_key]
    type_pair = random.choice(typography)

    # Output
    print(f"--- UI Design Brief: {archetype} ({theme_key.replace('_', ' ').title()}) ---")
    print(f"1. Surface Commitment: {archetype}")
    print("\n2. CSS Palette Tokens:")
    for k, v in palette.items():
        print(f"   --color-{k}: {v};")
    print(f"\n3. Typography: {type_pair[0]} (UI) + {type_pair[1]} (Mono)")
    print("\n4. Anti-Slop Directives:")
    print("   - BAN: Purple/Pink gradients.")
    print("   - BAN: Unearned glassmorphism.")
    print("   - BAN: Accent left-rails (use semantic layouts).")
    print("   - BAN: Icon toppers.")
    print("\n5. 10-Point Slop Diagnostic Checklist:")
    checklist = [
        "Contrast ratio >= 4.5:1?", "Dynamic font sizing?", "No nested shadow bloat?",
        "Consistent border-radius?", "Semantic spacing (rem)?", "Logical heading hierarchy?",
        "Zero-latency interaction feedback?", "Accessible tap targets?", 
        "No redundant decorative containers?", "Fluid responsive break-points?"
    ]
    for i, item in enumerate(checklist, 1):
        print(f"   {i}. {item}")

if __name__ == "__main__":
    generate_brief()
