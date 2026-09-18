# services/lecture_mode/slide_parser.py
from pathlib import Path
import re
import subprocess
from collections import Counter

# Standard English stop words to filter out common conversational/generic terms
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "lecture", "slide", "slides", "page", "university",
    "alberta", "department", "chapter", "section", "part", "example", "outline",
    "overview", "summary", "review", "question", "questions", "answer", "answers",
    "today", "next", "class", "course", "instructor", "professor", "edition",
    "copyright", "reserved", "rights"
}

def extract_text_from_pdf(pdf_path: Path | str) -> str:
    """
    Extracts text from a PDF file using macOS native PDFKit via a Swift one-liner.
    Requires no third-party python dependencies and runs with native speed.
    """
    path_obj = Path(pdf_path).expanduser().resolve()
    if not path_obj.exists():
        raise FileNotFoundError(f"PDF file not found: {path_obj}")

    swift_script = f"""
    import PDFKit
    import Foundation
    let url = URL(fileURLWithPath: "{path_obj}")
    if let doc = PDFDocument(url: url) {{
        var fullText = ""
        for i in 0..<doc.pageCount {{
            if let page = doc.page(at: i), let str = page.string {{
                fullText += str + "\\n"
            }}
        }}
        print(fullText)
    }}
    """
    try:
        proc = subprocess.run(
            ["swift", "-e", swift_script],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
        return proc.stdout
    except Exception as e:
        # Fallback to empty string if swift extraction fails
        return ""

def extract_terms_of_art(text: str, max_terms: int = 40) -> list[str]:
    """
    Extracts key academic terms of art, capitalized multi-word phrases,
    and domain-specific vocabulary from lecture text.
    """
    if not text:
        return []

    # 1. Capture Title Case / Proper Noun phrases (e.g. "Dijkstra's Algorithm", "Binary Search Tree")
    phrase_pattern = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b")
    phrases = phrase_pattern.findall(text)

    # 2. Capture Technical Acronyms (e.g. "CPU", "RAM", "FIFO", "LRU", "BFS")
    acronym_pattern = re.compile(r"\b[A-Z]{2,6}\b")
    acronyms = acronym_pattern.findall(text)

    # 3. Capture individual distinctive words
    word_pattern = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]{3,}\b")
    words = word_pattern.findall(text)

    term_counts: Counter[str] = Counter()

    for phrase in phrases:
        clean_p = phrase.strip()
        words_in_p = clean_p.lower().split()
        if not all(w in STOP_WORDS for w in words_in_p):
            term_counts[clean_p] += 3  # Higher weight for multi-word technical concepts

    for acr in acronyms:
        if acr.lower() not in STOP_WORDS:
            term_counts[acr] += 2

    for w in words:
        w_lower = w.lower()
        if w_lower not in STOP_WORDS and not w.isdigit():
            # Keep original capitalization if capitalized
            term_counts[w] += 1

    # Filter out single-character or duplicate terms
    ranked_terms: list[str] = []
    seen_lower = set()
    for term, _ in term_counts.most_common():
        t_low = term.lower()
        if t_low not in seen_lower and len(term) > 2:
            seen_lower.add(t_low)
            ranked_terms.append(term)
            if len(ranked_terms) >= max_terms:
                break

    return ranked_terms

def build_whisper_initial_prompt(terms: list[str], max_chars: int = 350) -> str:
    """
    Formats the extracted terms of art into a comma-separated vocabulary
    prompt that primes Whisper's attention weights for domain-specific terminology.
    """
    if not terms:
        return ""

    prompt_parts = []
    current_len = 0
    for term in terms:
        if current_len + len(term) + 2 > max_chars:
            break
        prompt_parts.append(term)
        current_len += len(term) + 2

    return ", ".join(prompt_parts)
