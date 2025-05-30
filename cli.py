import argparse
from core import api_checker, var_checker, import_checker, trace_analyzer, keyword_scanner

def main():
    parser = argparse.ArgumentParser(description="Smart Error Assistant")
    parser.add_argument("path", help="Path to the project folder")
    parser.add_argument("--check-api", action="store_true", help="Check for broken API calls")
    parser.add_argument("--check-vars", action="store_true", help="Check for undefined variables")
    parser.add_argument("--check-imports", action="store_true", help="Check for import issues")
    parser.add_argument("--trace", action="store_true", help="Analyze stack trace")
    parser.add_argument("--keywords", action="store_true", help="Search for common error keywords")

    args = parser.parse_args()

    # If no flags given, run all checks by default (optional)
    if not any([args.check_api, args.check_vars, args.check_imports, args.trace, args.keywords]):
        print("⚠️ No checks specified, running all checks by default.")
        args.check_api = args.check_vars = args.check_imports = args.trace = args.keywords = True

    if args.check_api:
        print("\n=== Running API Checker ===")
        api_checker.run(args.path)
    if args.check_vars:
        print("\n=== Running Undefined Variable Checker ===")
        var_checker.run(args.path)
    if args.check_imports:
        print("\n=== Running Import Checker ===")
        import_checker.run(args.path)
    if args.trace:
        print("\n=== Running Stack Trace Analyzer ===")
        trace_analyzer.run(args.path)
    if args.keywords:
        print("\n=== Running Keyword Scanner ===")
        keyword_scanner.run(args.path)

if __name__ == "__main__":
    main()
