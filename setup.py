"""Configuration du package."""

from setuptools import setup, find_packages

setup(
    name="sadie",
    version="0.2.1",
    description="Advanced Trading Data Collection and Analysis System",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/sadie",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "websockets>=12.0",
        "redis>=5.0.1",
        "prometheus-client>=0.19.0",
        "numpy>=1.26.2",
        "pandas>=2.1.3",
        "pydantic>=2.5.2",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "analysis": [
            "scikit-learn>=1.3.2",
            "statsmodels>=0.14.0",
            "ta-lib>=0.4.28",
        ],
        "database": [
            "sqlalchemy>=2.0.23",
            "alembic>=1.12.1",
            "psycopg2-binary>=2.9.9",
        ],
        "test": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "pytest-timeout>=2.2.0",
            "pytest-xdist>=3.5.0",
        ],
        "dev": [
            "black>=23.11.0",
            "isort>=5.12.0",
            "mypy>=1.7.1",
            "pylint>=3.0.2",
            "pre-commit>=3.5.0",
        ],
        "debug": [
            "debugpy>=1.8.0",
            "ipython>=8.17.2",
        ],
        "docs": [
            "mkdocs>=1.5.3",
            "mkdocs-material>=9.4.14",
            "mkdocstrings[python]>=0.24.0",
            "mkdocs-material-extensions>=1.3.1",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
) 