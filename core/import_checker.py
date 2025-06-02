import os
import ast
import importlib.util
import re
from langchain.tools import tool

PY_EXT = ".py"
JS_TS_EXT = (".js", ".ts", ".jsx", ".tsx")
EXCLUDED_DIRS = {"env", "venv", "__pycache__", ".git", "site-packages"}

@tool
def check_import_errors(path: str) -> str:
    """LangChain tool: Scan for broken or mistyped API endpoints."""
    print("🔍 Running API Checker...")
    results = run(path)

    if not results:
        return "✅ No API issues found."

    # Convert list of results to single string
    output = "\n".join(map(str, results))
    print(f"Returning:\n{output}")
    return output



def check_imports_in_python(filepath: str):
    issues = []
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read(), filename=filepath)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if not module_exists(alias.name):
                            issues.append((alias.name, node.lineno))
                elif isinstance(node, ast.ImportFrom):
                    if node.module and not module_exists(node.module):
                        issues.append((node.module, node.lineno))
    except Exception as e:
        issues.append((f"❌ Error parsing {filepath}", str(e)))
    return issues

def check_imports_in_jsts(filepath: str):
    issues = []
    import_pattern = re.compile(r"(?:import\s.*?from\s+['\"](.*?)['\"]|require\(['\"](.*?)['\"]\))")
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for i, line in enumerate(file.readlines()):
                matches = import_pattern.findall(line)
                for match in matches:
                    module = match[0] or match[1]
                    if not is_node_module_installed(module):
                        issues.append((module, i + 1))
    except Exception as e:
        issues.append((f"❌ Error reading {filepath}", str(e)))
    return issues

def is_node_module_installed(module_name: str) -> bool:
    return os.path.exists(os.path.join("node_modules", module_name))

def module_exists(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False

def run(path: str) -> list[str]:
    messages = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for filename in files:
            filepath = os.path.join(root, filename)
            issues = []
            if filename.endswith(PY_EXT):
                issues = check_imports_in_python(filepath)
            elif filename.endswith(JS_TS_EXT):
                issues = check_imports_in_jsts(filepath)

            for mod, line in issues:
                messages.append(f"{filepath}:{line} -> Missing or invalid import: '{mod}'")
    return messages
