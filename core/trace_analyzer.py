import os
import re
from langchain.tools import tool

# Patterns for different languages
TRACE_PATTERNS = {
    "python": re.compile(r'File "(.+?)", line (\d+), in (.+)'),
    "javascript": re.compile(r'at .+ \((.+):(\d+):(\d+)\)'),  # capture file, line, col
    "java": re.compile(r'at .+\((.+):(\d+)\)'),
}

def parse_trace(trace, lang):
    pattern = TRACE_PATTERNS.get(lang)
    if not pattern:
        return []
    return pattern.findall(trace)

def get_code_context(filepath, line_no, context=3):
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return f"Could not read file {filepath}: {e}"

    start = max(0, int(line_no) - context - 1)
    end = min(len(lines), int(line_no) + context)
    snippet = ''.join(lines[start:end])
    return f"\n--- {filepath}:{line_no} ---\n{snippet}"

def detect_language(trace):
    """
    Try all patterns and return language with most matches.
    """
    scores = {}
    for lang, pattern in TRACE_PATTERNS.items():
        matches = pattern.findall(trace)
        scores[lang] = len(matches)
    best_lang = max(scores, key=scores.get)
    if scores[best_lang] == 0:
        return None
    return best_lang

@tool
def analyze_stack_trace(trace_or_path: str) -> str:
    """
    Analyze a stack trace (string or file path), auto-detect language,
    and return code context for each frame.
    """
    if os.path.isfile(trace_or_path):
        try:
            with open(trace_or_path, 'r', encoding='utf-8') as f:
                trace = f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    else:
        trace = trace_or_path

    lang = detect_language(trace)
    if not lang:
        return "Could not detect stack trace language or no frames found."

    frames = parse_trace(trace, lang)
    if not frames:
        return "No valid stack trace frames found."

    report = [f"🧵 Stack Trace Analysis (detected language: {lang}):"]
    for frame in frames:
        if lang == "python":
            filepath, line, fn = frame
        elif lang == "javascript":
            filepath, line, col = frame
        elif lang == "java":
            filepath, line = frame
        else:
            continue  # unsupported

        context = get_code_context(filepath, int(line))
        report.append(context)

    return "\n".join(report)


# Optional CLI run method (for your existing CLI)
def run(path):
    trace_file = os.path.join(path, "stacktrace.log")
    if not os.path.exists(trace_file):
        print("❌ No stacktrace.log file found.")
        return
    result = analyze_stack_trace(trace_file)
    print(result)
