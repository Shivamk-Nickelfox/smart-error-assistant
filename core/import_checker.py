# core/import_checker.py
import os
import ast
import importlib.util
import re

PY_EXT = ".py"
JS_TS_EXT = (".js", ".ts", ".jsx", ".tsx")

def check_imports_in_python(filepath):
    issues = []
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
    return issues

def check_imports_in_jsts(filepath):
    issues = []
    import_pattern = re.compile(r"(?:import\s.*?from\s+['\"](.*?)['\"]|require\(['\"](.*?)['\"]\))")
    with open(filepath, "r", encoding="utf-8") as file:
        for i, line in enumerate(file.readlines()):
            matches = import_pattern.findall(line)
            for match in matches:
                module = match[0] or match[1]
                if not is_node_module_installed(module):
                    issues.append((module, i + 1))
    return issues

def is_node_module_installed(module_name):
    return os.path.isdir(f"node_modules/{module_name}")

def module_exists(name):
    return importlib.util.find_spec(name) is not None

def run(path):
    print("\n📦 Checking for import issues...")
    for root, _, files in os.walk(path):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filename.endswith(PY_EXT):
                issues = check_imports_in_python(filepath)
            elif filename.endswith(JS_TS_EXT):
                issues = check_imports_in_jsts(filepath)
            else:
                continue

            for mod, line in issues:
                print(f"{filepath}:{line} -> Missing or invalid import: '{mod}'")
