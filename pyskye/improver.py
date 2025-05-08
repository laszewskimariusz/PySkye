import os
import sys
import importlib
from typing import List, Optional
from llama_cpp import Llama
from git import Repo
from pyskye.loader import load_project
from pyskye.analyzer import analyze_files


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
        raw = input("Enter the Llama model path or export command: ").strip()
        # Extract path after '=' if present
        if '=' in raw:
            raw = raw.rsplit('=', 1)[1]
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
        n_threads=os.cpu_count(),
    )(model_path=model_path, n_threads=os.cpu_count())


def path_to_module(path: str, base_path: str) -> str:
    rel = os.path.relpath(path, base_path)
    return rel.replace(os.sep, ".")[:-3]


def generate_patch(target_files: List[str], prompt: str) -> str:
    """
    Generate unified diff via local LLM.
    """
    llm = get_local_llm()
    files_list = ", ".join(target_files)
    full_prompt = (
        "You are an AI assistant generating unified diffs.\n"
        f"Files: {files_list}\n"
        f"Request: {prompt}\n"
        "Output diff only."
    )
    resp = llm(full_prompt, max_tokens=2048, stop=["```"], temperature=0.0)
    choices = resp.get("choices", [])
    text = choices[0].get("text", "") if choices else ""
    return text.strip()


def apply_patch(patch: str, repo_path: str) -> None:
    repo = Repo(repo_path)
    try:
        repo.git.apply("--whitespace=fix", input=patch)
        print("Patch applied successfully.")
    except Exception as e:
        print(f"Failed to apply patch: {e}")


def reload_changed_modules(changed_files: List[str], base_path: str) -> None:
    for path in changed_files:
        module = path_to_module(path, base_path)
        if module in sys.modules:
            importlib.reload(sys.modules[module])
            print(f"Reloaded module: {module}")


def select_file(files: List[str]) -> Optional[List[str]]:
    print("Available files:")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")
    choice = input("Select file number or 'all'/'exit': ").strip().lower()
    if choice in ("exit", "quit"):
        return None
    if choice == "all":
        return files
    if choice.isdigit():
        i = int(choice)
        if 1 <= i <= len(files):
            return [files[i-1]]
    print("Invalid selection, try again.")
    return select_file(files)


def interactive_improve(path: str) -> None:
    print(f"Starting interactive improvement in '{path}'")
    files = load_project(path)

    while True:
        target = select_file(files)
        if target is None:
            print("Exiting improvement session.")
            break
        prompt = input("Describe change or feature: ").strip()
        if not prompt:
            print("Prompt cannot be empty.")
            continue
        print(f"Generating patch for: {', '.join(target)}...")
        patch = generate_patch(target, prompt)
        if not patch:
            print("No patch received; refine prompt.")
            continue
        print("Applying patch...")
        apply_patch(patch, path)
        print("Reloading changed modules...")
        reload_changed_modules(target, path)
        print("Re-running static analysis...\n")
        issues = analyze_files(target)
        if issues:
            print("Issues in updated files:")
            for issue in issues:
                print(issue)
            print("Refine prompt or select another file, or 'exit'.")
        else:
            print("No issues found in updated files!")
            cont = input("Apply another improvement? (yes/no): ").strip().lower()
            if cont not in ('yes', 'y'):
                print("Exiting improvement session.")
                break