import os
import sys
import importlib
from typing import List, Optional

import openai
from git import Repo

from pyskye.loader import load_project
from pyskye.analyzer import analyze_files


# Wymagamy ChatCompletion – jeśli go nie ma, prosimy o upgrade
if not hasattr(openai, "ChatCompletion"):
    raise ImportError(
        "Your openai package is outdated. "
        "Please run 'pip install --upgrade openai'."
    )


def path_to_module(path: str, base_path: str) -> str:
    rel = os.path.relpath(path, base_path)
    return rel.replace(os.sep, ".")[:-3]


def generate_patch(
    target_files: List[str], prompt: str
) -> str:
    """
    Use OpenAI to generate a unified diff for specific files.
    """
    files_list = ", ".join(target_files)
    content = (
        f"Target files: {files_list}\n"
        f"Request: {prompt}\n"
        "Generate a unified diff for only these files."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a code-fixing AI that returns diffs "
                    "for requested files only."
                ),
            },
            {"role": "user", "content": content},
        ],
    )
    return response.choices[0].message.content


def apply_patch(patch: str, repo_path: str) -> None:
    """
    Apply a unified diff to the repo via git apply.
    """
    repo = Repo(repo_path)
    try:
        repo.git.apply("--whitespace=fix", input=patch)
        print("Patch applied successfully.")
    except Exception as e:
        print(f"Failed to apply patch: {e}")


def reload_changed_modules(
    changed_files: List[str], base_path: str
) -> None:
    """
    Reload only the modified modules without restarting.
    """
    for path in changed_files:
        mod = path_to_module(path, base_path)
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
            print(f"Reloaded module: {mod}")


def select_file(files: List[str]) -> Optional[List[str]]:
    """
    Let the user pick one file or 'all'; returns list or None.
    """
    print("Available files:")
    for idx, f in enumerate(files, 1):
        print(f"  {idx}. {f}")
    choice = input(
        "Select number (or 'all', 'exit'): "
    ).strip().lower()
    if choice in ("exit", "quit"):
        return None
    if choice == "all":
        return files
    if choice.isdigit():
        i = int(choice)
        if 1 <= i <= len(files):
            return [files[i - 1]]
    print("Invalid selection, try again.")
    return select_file(files)


def interactive_improve(path: str) -> None:
    """
    Loop: select files, describe change, generate+apply patch,
    reload modules and re-run analysis on updated files.
    """
    print(f"Starting interactive improvement in '{path}'")
    files = load_project(path)

    while True:
        target = select_file(files)
        if target is None:
            print("Exiting improvement session.")
            break

        prompt = input("Describe the change or feature: ").strip()
        if not prompt:
            print("Prompt cannot be empty.")
            continue

        print(f"Generating patch for: {', '.join(target)}...")
        patch = generate_patch(target, prompt)
        if not patch.strip():
            print("No patch received. Refine your prompt.")
            continue

        print("Applying patch...")
        apply_patch(patch, path)

        print("Reloading changed modules...")
        reload_changed_modules(target, path)

        print(
            "Re-running static analysis on updated files...\n"
        )
        issues = analyze_files(target)
        if issues:
            print("Issues found in updated files:")
            for issue in issues:
                print(issue)
            print(
                "Refine prompt, select another file, "
                "or type 'exit'."
            )
        else:
            print("No issues found!")
            cont = input(
                "Apply another improvement? (y/n): "
            ).strip().lower()
            if cont not in ("y", "yes"):
                print("Exiting improvement session.")
                break

