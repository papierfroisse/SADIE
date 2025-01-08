"""
Configuration du package SADIE.
"""

from setuptools import setup, find_packages

# Lecture du fichier README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Lecture des dépendances
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="sadie",
    version="0.1.1",
    description="Système d'Analyse et de Décision pour l'Investissement en Cryptomonnaies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Papierfroisse",
    author_email="papierfroisse@example.com",
    url="https://github.com/papierfroisse/SADIE",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black",
            "flake8",
            "isort",
            "mypy",
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "sphinx",
            "sphinx-rtd-theme"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    keywords=[
        "cryptocurrency",
        "trading",
        "machine learning",
        "sentiment analysis",
        "technical analysis",
        "portfolio management"
    ],
    project_urls={
        "Bug Reports": "https://github.com/papierfroisse/SADIE/issues",
        "Source": "https://github.com/papierfroisse/SADIE"
    },
    entry_points={
        "console_scripts": [
            "sadie=sadie.cli:main"
        ]
    }
)
