# PySkye Project Skeleton

Repository: https://github.com/laszewskimariusz/PySkye

File Tree:

```
.
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
├── pyskye
│   ├── __init__.py
│   ├── main.py
│   ├── loader.py
│   ├── analyzer.py
│   └── search.py
```

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

## Installation

Install in editable mode to expose the `pyskye` package:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements.txt
```
````

## Usage

After installation, invoke via CLI:

```bash
pyskye analyze .
```

```

```
