# core/api_checker.py
import os
import re
import requests
from langchain.tools import tool

API_PATTERN = re.compile(r'https?://[^\s\'"]+')

@tool
def check_api_errors(path: str) -> str:
    """
    Scan for broken or mistyped API endpoint calls by finding URLs and validating their HTTP responses.
    """
    results = run(path)
    return "\n".join(results) if results else "No API issues found."

def is_valid_url(url: str) -> bool:
    return url.startswith("http") and "." in url and not url.endswith(".")

def check_http_status(url: str) -> str:
    try:
        response = requests.head(url, timeout=5)
        if response.status_code in {400, 401, 403, 404, 429, 500, 503}:
            return f"{response.status_code} {response.reason}"
    except requests.RequestException as e:
        return f"Request error: {str(e)}"
    return ""  # No error

def run(path: str) -> list[str]:
    error_lines = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith((".js", ".ts", ".py")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            matches = API_PATTERN.findall(line)
                            for match in matches:
                                if is_valid_url(match):
                                    error = check_http_status(match)
                                    if error:
                                        error_lines.append(f"{filepath}:{i+1} => {match} => ❌ {error}")
                                else:
                                    error_lines.append(f"{filepath}:{i+1} => {match} => ❌ Invalid URL format")
                except Exception as e:
                    error_lines.append(f"Error reading {filepath}: {str(e)}")

    return error_lines
