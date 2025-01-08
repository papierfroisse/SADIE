from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sadie",
    version="0.1.1",
    author="PapierFroisse",
    author_email="papierfroisse@example.com",
    description="Système d'Analyse et de Décision pour l'Investissement en cryptomonnaies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/papierfroisse/SADIE",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-cov>=2.12.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.9b0",
            "flake8>=3.9.2",
            "isort>=5.9.3",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
            "sphinx>=4.2.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sadie=sadie.cli:main",
        ],
    },
) 