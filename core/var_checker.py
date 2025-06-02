import os
import ast
from langchain.tools import tool
import builtins

class UndefinedVarVisitor(ast.NodeVisitor):
    def __init__(self):
        self.scopes = [set()]  # Stack of variable scopes
        self.undefined = []
        self.builtins = set(dir(builtins))

    def current_scope(self):
        return self.scopes[-1]

    def is_defined(self, name):
        return any(name in scope for scope in reversed(self.scopes)) or name in self.builtins

    def visit_FunctionDef(self, node):
        self.current_scope().add(node.name)  # Add function name to enclosing scope
        self.scopes.append(set(arg.arg for arg in node.args.args))
        self.generic_visit(node)
        self.scopes.pop()

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        self.current_scope().add(node.name)
        self.scopes.append(set())
        self.generic_visit(node)
        self.scopes.pop()

    def visit_Assign(self, node):
        self.generic_visit(node.value)
        for target in node.targets:
            self._handle_target(target)

    def visit_AnnAssign(self, node):
        if node.value:
            self.generic_visit(node.value)
        self._handle_target(node.target)

    def visit_For(self, node):
        self._handle_target(node.target)
        self.generic_visit(node)

    def visit_With(self, node):
        for item in node.items:
            if item.optional_vars:
                self._handle_target(item.optional_vars)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.current_scope().add(alias.asname or alias.name.split('.')[0])

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.current_scope().add(alias.asname or alias.name.split('.')[0])

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if not self.is_defined(node.id):
                self.undefined.append((node.id, node.lineno))
        elif isinstance(node.ctx, ast.Store):
            self.current_scope().add(node.id)
        self.generic_visit(node)

    def _handle_target(self, target):
        if isinstance(target, ast.Name):
            self.current_scope().add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._handle_target(elt)


def find_undefined_vars_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
        visitor = UndefinedVarVisitor()
        visitor.visit(tree)
        return visitor.undefined
    except Exception as e:
        return [("Parsing error", str(e))]


def scan_directory_for_undefined_vars(path):
    issues = {}
    exclude_dirs = {"env", "venv", "__pycache__", "site-packages", ".git", "node_modules", "build", "dist"}
    skip_files = {"api_checker.py", "import_checker.py", "keyword_scanner.py", "trace_analyzer.py", "var_checker.py", "cli.py","file_loader.py"}

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for filename in files:
            if filename in skip_files:
                continue
            # Process only Python files
            if filename.endswith(".py"):
                filepath = os.path.join(root, filename)
                result = find_undefined_vars_in_file(filepath)
                if result:
                    issues[filepath] = result
    return issues


@tool
def check_undefined_variables(path: str) -> str:
    """
    LangChain Tool: Check Python files in the given directory for undefined variables.
    """
    issues = scan_directory_for_undefined_vars(path)
    if not issues:
        return "✅ No undefined variables found."

    report = ["🧠 Undefined Variables Detected:"]
    for file, vars in issues.items():
        for var, line in vars:
            if isinstance(line, int):
                report.append(f"{file}:{line} -> Undefined variable: '{var}'")
            else:
                report.append(f"{file} -> {var}: {line}")

    output = "\n".join(report)
    print(output)  # Optional: for debugging
    return output



# Optional CLI for local testing
def run(path):
    print(check_undefined_variables(path))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        print("❗ Please provide a path to scan.")
