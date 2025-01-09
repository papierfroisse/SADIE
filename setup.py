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
    name="sadie",
    version="0.1.0",
    description="Système d'Analyse de Données et d'Intelligence Économique",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Radio France",
    author_email="opensource@radiofrance.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "sadie=sadie.cli:main",
        ],
    },
    project_urls={
        "Homepage": "https://github.com/radiofrance/sadie",
        "Documentation": "https://sadie.readthedocs.io/",
        "Source": "https://github.com/radiofrance/sadie",
        "Tracker": "https://github.com/radiofrance/sadie/issues",
    },
)
