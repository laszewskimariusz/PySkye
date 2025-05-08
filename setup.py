from setuptools import setup, find_packages

setup(
    name="pyskye",
    version="0.1.0",
    description="Self-improving AI code analyzer for Apple Silicon",
    author="Mariusz Laszewski",
    packages=find_packages(),
    install_requires=[
        "openai",
        "llama-cpp-python",
        "gitpython",
        "requests",
        "flake8",
        "mypy",
    ],
    entry_points={
        "console_scripts": [
            "pyskye=pyskye.main:main",
        ],
    },
)