import os


def load_project(path: str):
    """
    Recursively collect all .py files in a directory, ignoring venv, .git, and __pycache__.
    """
    py_files = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ("venv", ".git", "__pycache__")]
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files