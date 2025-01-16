"""Setup script for the sadie package."""

import os
from typing import Dict, List

from setuptools import find_packages, setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

def _read_requirements(filename: str) -> List[str]:
    """Read requirements from file."""
    with open(os.path.join(HERE, "requirements", filename)) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Get requirements
install_requires = _read_requirements("base.txt")
extras_require: Dict[str, List[str]] = {
    "dev": _read_requirements("dev.txt"),
    "prod": _read_requirements("prod.txt"),
}

# Get the long description from the README file
with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="SADIE",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "asyncpg",
        "python-dotenv",
        "aiohttp",
        "pandas",
        "numpy",
        "pytest",
        "pytest-asyncio",
        "pytest-cov"
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "mypy",
            "isort"
        ]
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="SADIE - Système Avancé de Distribution d'Information et d'Événements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/SADIE",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ]
)
