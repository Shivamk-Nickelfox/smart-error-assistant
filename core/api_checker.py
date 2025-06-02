import os
import re
import requests
from langchain.tools import tool

EXCLUDED_DIRS = {"env", "venv", "__pycache__", ".git", "node_modules", "site-packages"}
API_PATTERN = re.compile(r'https?://[^\s\'"]+')

@tool
def check_api_errors(path: str) -> str:
    """LangChain tool: Scan for broken or mistyped API endpoints."""
    print("🔍 Running API Checker...")
    print(f"Scanning directory: {path}")
    results = run(path)
    print(results)
    return "\n".join(results) if results else "✅ No API issues found."

def is_valid_url(url: str) -> bool:
    return url.startswith("http") and "." in url and not url.endswith(".")

def check_http_status(url: str) -> str:
    try:
        response = requests.head(url, timeout=3)
        if response.status_code >= 400:
            return f"{response.status_code} {response.reason}"
    except requests.RequestException as e:
        return f"❌ Request error: {str(e)}"
    return ""

def run(path: str) -> list[str]:
    error_lines = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith((".js", ".ts", ".py")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f):
                            for match in API_PATTERN.findall(line):
                                if is_valid_url(match):
                                    error = check_http_status(match)
                                    if error:
                                        error_lines.append(f"{filepath}:{i+1} => {match} => {error}")
                                else:
                                    error_lines.append(f"{filepath}:{i+1} => {match} => Invalid URL format")
                except Exception as e:
                    error_lines.append(f"{filepath} => ❌ Error reading file: {e}")
    return error_lines
