import subprocess
from typing import List


def analyze_files(files: List[str]) -> List[str]:
    """
    Run flake8 and mypy on given list of files and collect issues.
    Returns a list of issue strings.
    """
    issues = []

    # Run flake8
    try:
        result = subprocess.run(
            ["flake8"] + files,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.stdout:
            issues.extend(result.stdout.strip().splitlines())
    except FileNotFoundError:
        issues.append("flake8 is not installed or not found in PATH.")

    # Run mypy
    try:
        result = subprocess.run(
            ["mypy"] + files,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.stdout:
            issues.extend(result.stdout.strip().splitlines())
    except FileNotFoundError:
        issues.append("mypy is not installed or not found in PATH.")

    return issues