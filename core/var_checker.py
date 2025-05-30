# core/var_checker.py
import os
import ast
from langchain.tools import tool

class UndefinedVarVisitor(ast.NodeVisitor):
    def __init__(self):
        self.defined = set()
        self.undefined = []

    def visit_FunctionDef(self, node):
        for arg in node.args.args:
            self.defined.add(arg.arg)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined.add(target.id)
        self.generic_visit(node)

    def visit_For(self, node):
        if isinstance(node.target, ast.Name):
            self.defined.add(node.target.id)
        self.generic_visit(node)

    def visit_With(self, node):
        for item in node.items:
            if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                self.defined.add(item.optional_vars.id)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.defined.add(alias.asname or alias.name)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.defined.add(alias.asname or alias.name)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id not in self.defined:
            self.undefined.append((node.id, node.lineno))
        self.generic_visit(node)

def find_undefined_vars_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source, filename=filepath)
    visitor = UndefinedVarVisitor()
    visitor.visit(tree)
    return visitor.undefined

def scan_directory_for_undefined_vars(path):
    issues = {}
    for root, _, files in os.walk(path):
        for filename in files:
            if filename.endswith(".py"):
                filepath = os.path.join(root, filename)
                result = find_undefined_vars_in_file(filepath)
                if result:
                    issues[filepath] = result
    return issues

@tool
def check_undefined_variables(path: str) -> str:
    """
    Check Python files in the given directory for undefined variables.
    """
    issues = scan_directory_for_undefined_vars(path)
    if not issues:
        return "✅ No undefined variables found."

    report = ["🧠 Undefined Variables Detected:"]
    for file, vars in issues.items():
        for var, line in vars:
            report.append(f"{file}:{line} -> Undefined variable: '{var}'")
    return "\n".join(report)

# Optional CLI-compatible run function
def run(path):
    print(check_undefined_variables(path))
