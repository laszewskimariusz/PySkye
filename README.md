# PySkye Project Skeleton

Repository: https://github.com/laszewskimariusz/PySkye

File Tree:

```
.
├── .gitignore
├── README.md
├── requirements.txt
├── pyskye
│   ├── __init__.py
│   ├── main.py
│   ├── loader.py
│   ├── analyzer.py
│   └── search.py
```

Contents:

--- .gitignore ---

```
__pycache__/
venv/
.env
```

--- README.md ---

````markdown
# PySkye

PySkye is a self-improving AI code analyzer designed to run on Apple Silicon (M1/M2).

## Features

- Recursively loads Python source files
- Static analysis integration (flake8, mypy)
- LLM-driven code review and patch generation
- Web-search integration for code improvement suggestions

## Getting Started

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
````

### Usage

```bash
pyskye analyze .
```

```

--- requirements.txt ---
```

openai
gitpython
requests

````

--- pyskye/__init__.py ---
```python
# PySkye package
````

--- pyskye/main.py ---

```python
#!/usr/bin/env python3
import argparse
from pyskye.loader import load_project


def main():
    parser = argparse.ArgumentParser(
        prog="pyskye",
        description="PySkye - Self-improving AI code analyzer"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze the project code")

    args = parser.parse_args()

    if args.command == "analyze":
        files = load_project(".")
        print(f"Loaded {len(files)} Python files:\n", "\n".join(files))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

--- pyskye/loader.py ---

```python
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
```

--- pyskye/analyzer.py ---

```python
# Placeholder for static analysis integration
```

--- pyskye/search.py ---

```python
# Placeholder for web-search integration
```
