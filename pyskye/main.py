import argparse
import sys
from pyskye.loader import load_project
from pyskye.analyzer import analyze_files
from pyskye.improver import interactive_improve
import os
from llama_cpp import Llama


def main():
    parser = argparse.ArgumentParser(
        prog="pyskye",
        description="PySkye - Self-improving AI code analyzer and improver"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze the project code"
    )
    analyze_parser.add_argument(
        "path", nargs="?", default=".",
        help="Path to the project directory"
    )

    improve_parser = subparsers.add_parser(
        "improve", help="Interactively request code changes and apply improvements"
    )
    improve_parser.add_argument(
        "path", nargs="?", default=".",
        help="Path to the project directory"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        files = load_project(args.path)
        print(f"Loaded {len(files)} Python files in '{args.path}':")
        for f in files:
            print(f"  - {f}")
        print("\nRunning static analysis...\n")
        issues = analyze_files(files)
        if issues:
            print("Issues found:")
            for issue in issues:
                print(issue)
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


def get_local_llm() -> Llama:
    """
    Initialize a local LLM using llama-cpp-python.
    Priority:
      1. LLAMA_MODEL_PATH env var
      2. .pyskye/config.json
      3. ~/models/llama-2-7b.ggml.bin
    Prompts and saves if unset.
    """
    # 1. Environment variable
    model_path = os.getenv("LLAMA_MODEL_PATH")

    # 2. Config file
    cfg_dir = os.path.join(os.getcwd(), ".pyskye")
    cfg_file = os.path.join(cfg_dir, "config.json")
    if not model_path and os.path.isfile(cfg_file):
        try:
            import json
            cfg = json.load(open(cfg_file))
            model_path = cfg.get("model_path")
        except Exception:
            pass

    # 3. Default location
    if not model_path:
        default = os.path.expanduser(
            "~/models/llama-2-7b.ggml.bin"
        )
        if os.path.isfile(default):
            model_path = default

    # 4. Prompt if still unset
    if not model_path:
        raw = input("Enter the Llama model path: ").strip()
        # Remove any leading or trailing quotes
        raw = raw.strip('"\'')
        expanded = os.path.expanduser(raw)
        if not expanded or not os.path.isfile(expanded):
            raise RuntimeError(
                f"Model path does not exist: {expanded}"
            )
        model_path = expanded
        # Save to config
        os.makedirs(cfg_dir, exist_ok=True)
        try:
            import json
            with open(cfg_file, "w") as f:
                json.dump({"model_path": model_path}, f, indent=2)
            print(f"Saved model path to {cfg_file}")
        except Exception as e:
            print(f"Warning: could not write config: {e}")

    # Final expansion
    model_path = os.path.expanduser(model_path)
    return Llama(
        model_path=model_path,
        n_threads=os.cpu_count()
    )


if __name__ == "__main__":
    main()