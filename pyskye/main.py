import argparse
import sys
from pyskye.loader import load_project
from pyskye.analyzer import analyze_files
from pyskye.improver import interactive_improve


def main():
    parser = argparse.ArgumentParser(
        prog="pyskye",
        description="PySkye - Self-improving AI code analyzer and improver"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze the project code"
    )
    analyze_parser.add_argument(
        "path", nargs="?", default=".", help="Path to the project directory"
    )

    # improve command
    improve_parser = subparsers.add_parser(
        "improve", help="Interactively request code changes and apply improvements"
    )
    improve_parser.add_argument(
        "path", nargs="?", default=".", help="Path to the project directory"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        files = load_project(args.path)
        print(f"Loaded {len(files)} Python files in '{args.path}':")
        for f in files:
            print(f"  - {f}")
        print("Running static analysis...")
        issues = analyze_files(files)
        if issues:
            print("Issues found:")
            for issue in issues:
                print(issue)
            # Ask user if they want to fix issues interactively
            choice = input("Fix issues interactively? (y/n): ").strip().lower()
            if choice in ('y', 'yes'):
                interactive_improve(args.path)
        else:
            print("No issues found by flake8 and mypy.")
    elif args.command == "improve":
        try:
            interactive_improve(args.path)
        except KeyboardInterrupt:
            print("\nImprovement session cancelled.")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
