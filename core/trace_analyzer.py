import os
import re
from langchain.tools import tool

# Regex patterns to detect stack frames by language
TRACE_PATTERNS = {
    "python": re.compile(r'File "(.+?)", line (\d+), in (.+)'),
    "javascript": re.compile(r'at .+ \((.+):(\d+):(\d+)\)'),  # file, line, column
    "java": re.compile(r'at .+\((.+):(\d+)\)'),
}

def detect_language(trace: str) -> str | None:
    """Detects the programming language based on stack trace patterns."""
    scores = {lang: len(pattern.findall(trace)) for lang, pattern in TRACE_PATTERNS.items()}
    best_lang = max(scores, key=scores.get)
    return best_lang if scores[best_lang] > 0 else None

def parse_trace(trace: str, lang: str):
    """Parse trace using the appropriate regex for the detected language."""
    pattern = TRACE_PATTERNS.get(lang)
    return pattern.findall(trace) if pattern else []

def get_code_context(filepath: str, line_no: int, context: int = 3) -> str:
    """Get surrounding lines for a specific line in a file."""
    if not os.path.exists(filepath):
        return f"❌ File not found: {filepath}"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return f"❌ Could not read file {filepath}: {e}"

    start = max(0, line_no - context - 1)
    end = min(len(lines), line_no + context)
    snippet = ''.join(lines[start:end])
    return f"\n📄 {filepath} (line {line_no}):\n{snippet}"

@tool
def analyze_stack_trace(trace_or_path: str) -> str:
    """
    LangChain Tool: Analyze a Python/JS/Java stack trace (raw string or file path),
    detect language, and return source code context for each frame.
    """
    if os.path.isfile(trace_or_path):
        try:
            with open(trace_or_path, 'r', encoding='utf-8') as f:
                trace = f.read()
        except Exception as e:
            return f"❌ Error reading file: {e}"
    else:
        trace = trace_or_path

    lang = detect_language(trace)
    if not lang:
        return "❌ Could not detect stack trace language."

    frames = parse_trace(trace, lang)
    if not frames:
        return "⚠️ No valid stack trace frames found."

    report = [f"🧵 Stack Trace Analysis (Detected: {lang})"]
    for frame in frames:
        try:
            if lang == "python":
                filepath, line, _ = frame
            elif lang == "javascript":
                filepath, line, _ = frame
            elif lang == "java":
                filepath, line = frame
            else:
                continue

            context = get_code_context(filepath, int(line))
            report.append(context)
        except Exception as e:
            report.append(f"⚠️ Error processing frame {frame}: {e}")
    
    return "\n".join(report)


# Optional CLI wrapper for testing locally
def run(path: str):
    trace_file = os.path.join(path, "stacktrace.log")
    if not os.path.exists(trace_file):
        print("❌ No stacktrace.log file found in the path.")
        return
    result = analyze_stack_trace(trace_file)
    print(result)
