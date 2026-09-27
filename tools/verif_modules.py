"""Vérifie quels modules sont disponibles dans l'environnement SADIE.

    .venv\\Scripts\\python.exe tools\\verif_modules.py
"""
import importlib.util

MODULES = [
    'pandas', 'numpy', 'scipy', 'aiohttp', 'websockets', 'fastapi',
    'asyncpg', 'redis', 'yaml', 'psutil', 'pytest', 'pytest_asyncio',
    'sadie',
]

presents = [m for m in MODULES if importlib.util.find_spec(m)]
manquants = [m for m in MODULES if not importlib.util.find_spec(m)]

print('    présents  : ' + ', '.join(presents))
print('    manquants : ' + (', '.join(manquants) if manquants else 'aucun'))