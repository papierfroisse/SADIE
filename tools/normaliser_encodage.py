"""Normalise l'encodage des fichiers texte : UTF-16 -> UTF-8.

Certains fichiers du dépôt ont été enregistrés en UTF-16 (BOM FF FE) alors que
Python lit les sources en UTF-8 : `SyntaxError: source code string cannot
contain null bytes`. Un fichier YAML dans le même cas est tout aussi inutilisable
(GitHub Actions refuse de lire un workflow qu'il ne peut pas décoder).

Le script couvre les sources Python **et** les fichiers texte du projet
(`.yml`, `.md`, `.json`, `.sh`…) et les convertit en UTF-8 sans BOM.

    .venv\\Scripts\\python.exe tools\\normaliser_encodage.py [--ecrire]

Sans `--ecrire`, le script se contente d'afficher ce qu'il ferait.
"""
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
EXCLUS = {'.git', 'old', '.venv', 'venv', 'node_modules', '__pycache__'}
BOMS = {b'\xff\xfe': 'utf-16-le', b'\xfe\xff': 'utf-16-be'}

# Extensions de fichiers texte : un fichier UTF-16 y est toujours un défaut.
# Les formats binaires (images, archives, bases) sont volontairement exclus.
EXTENSIONS = {
    '.py', '.pyi', '.yml', '.yaml', '.md', '.rst', '.txt', '.json', '.toml',
    '.ini', '.cfg', '.conf', '.sh', '.ps1', '.cmd', '.bat', '.html', '.css',
    '.js', '.ts', '.env', '.sql', '.csv',
}


def fichiers_a_corriger():
    for chemin in sorted(RACINE.rglob('*')):
        if not chemin.is_file() or chemin.suffix.lower() not in EXTENSIONS:
            continue
        if EXCLUS & set(chemin.relative_to(RACINE).parts):
            continue
        donnees = chemin.read_bytes()
        encodage = BOMS.get(donnees[:2])
        if encodage is None and b'\x00' in donnees:
            encodage = 'utf-16-le'  # ni BOM ni UTF-8 : on tente l'UTF-16LE
        if encodage:
            yield chemin, encodage, donnees


def main():
    ecrire = '--ecrire' in sys.argv
    total = 0
    for chemin, encodage, donnees in fichiers_a_corriger():
        relatif = chemin.relative_to(RACINE)
        try:
            texte = donnees.decode(encodage)
        except UnicodeDecodeError as err:
            print(f'  ! {relatif} : illisible en {encodage} ({err})')
            continue
        texte = texte.lstrip('\ufeff')
        total += 1
        if ecrire:
            chemin.write_text(texte, encoding='utf-8', newline='')
            print(f'  converti  {relatif}  ({encodage} -> utf-8, {len(texte)} caractères)')
        else:
            print(f'  à convertir  {relatif}  ({encodage}, {len(texte)} caractères)')

    if not total:
        print('  aucun fichier à corriger : tout est déjà en UTF-8.')
    elif not ecrire:
        print(f'\n  {total} fichier(s) à convertir — relancer avec --ecrire.')


if __name__ == '__main__':
    main()