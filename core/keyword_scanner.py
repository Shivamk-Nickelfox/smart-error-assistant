# core/keyword_scanner.py
import os
from difflib import SequenceMatcher
from langchain.tools import tool

# Common error patterns across languages
COMMON_ERRORS = [
    # Python errors
    "ModuleNotFoundError", "AttributeError", "TypeError", "NameError", "KeyError",
    "ValueError", "ImportError", "IndentationError", "SyntaxError",

    # JavaScript/TypeScript errors
    "ReferenceError", "TypeError", "SyntaxError", "RangeError",
    "Uncaught ReferenceError", "Cannot read property", "Module not found",
    "UnhandledPromiseRejectionWarning", "Unexpected token", "is not defined",

    # Framework-related
    "ReactDOM.render is not a function", "Cannot find module",
    "axios is not defined", "fetch is not defined",
    "Unknown provider", "Template parse error", "Zone.js error"
]

SUPPORTED_EXTENSIONS = [".py", ".ts", ".js", ".tsx", ".jsx", ".json"]

def fuzzy_match(a, b):
    return SequenceMatcher(None, a, b).ratio()

@tool
def scan_error_keywords(path: str) -> str:
    """
    Scan project files (.py, .js, .ts, etc.) for fuzzy matches to known error patterns.
    """
    results = run(path)
    return "\n".join(results) if results else "No error keywords found."

def run(path):
    print("\n🔍 Scanning files for common error keywords...")
    matches = []
    for root, _, files in os.walk(path):
        for filename in files:
            if any(filename.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
                        lines = file.readlines()
                        for i, line in enumerate(lines):
                            for err in COMMON_ERRORS:
                                score = fuzzy_match(err.lower(), line.lower())
                                if score > 0.7:
                                    match = f"{filepath}:{i+1} -> {line.strip()} (matched: {err}, score: {score:.2f})"
                                    print(match)
                                    matches.append(match)
                except Exception as e:
                    matches.append(f"{filepath} -> Error reading file: {e}")
    return matches
