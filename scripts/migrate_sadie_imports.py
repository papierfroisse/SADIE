#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de migration des imports SADIE vers sadie.
Ce script parcourt tous les fichiers Python dans le projet et remplace
les imports utilisant 'SADIE' par 'sadie' (en minuscules).
"""

import os
import re
import sys
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple


def create_backup(file_path: str) -> str:
    """
    Crée une sauvegarde du fichier.
    
    Args:
        file_path (str): Chemin du fichier à sauvegarder
        
    Returns:
        str: Chemin du fichier de sauvegarde
    """
    backup_dir = Path("old") / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    rel_path = Path(file_path).relative_to(Path.cwd())
    backup_path = backup_dir / rel_path
    
    # Créer les répertoires parents si nécessaire
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copier le fichier
    shutil.copy2(file_path, backup_path)
    
    return str(backup_path)


def find_sadie_imports(
    directory: str = ".", 
    exclude_dirs: List[str] = None
) -> List[Tuple[str, List[str]]]:
    """
    Trouve tous les fichiers Python contenant des imports SADIE.
    
    Args:
        directory (str): Répertoire racine à parcourir
        exclude_dirs (List[str]): Liste des répertoires à exclure
        
    Returns:
        List[Tuple[str, List[str]]]: Liste de tuples (chemin_fichier, liste_lignes_import)
    """
    if exclude_dirs is None:
        exclude_dirs = ["old", ".git", ".venv", "venv", "__pycache__", "build", "dist"]
    
    # Regexp pour les imports
    import_patterns = [
        re.compile(r"from\s+SADIE(\..+)?\s+import"),
        re.compile(r"import\s+SADIE(\..+)?"),
    ]
    
    files_with_imports = []
    
    for root, dirs, files in os.walk(directory):
        # Filtrer les répertoires exclus
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.readlines()
                    
                    sadie_import_lines = []
                    for i, line in enumerate(content):
                        for pattern in import_patterns:
                            if pattern.search(line):
                                sadie_import_lines.append((i, line))
                    
                    if sadie_import_lines:
                        files_with_imports.append((file_path, sadie_import_lines))
                
                except Exception as e:
                    print(f"⚠️ Erreur lors de la lecture de {file_path}: {str(e)}")
    
    return files_with_imports


def update_imports(
    file_path: str, 
    import_lines: List[Tuple[int, str]], 
    dry_run: bool = False
) -> bool:
    """
    Met à jour les imports SADIE en sadie dans un fichier.
    
    Args:
        file_path (str): Chemin du fichier à mettre à jour
        import_lines (List[Tuple[int, str]]): Liste de tuples (index_ligne, ligne_import)
        dry_run (bool): Si True, n'effectue pas les modifications
        
    Returns:
        bool: True si des modifications ont été effectuées, False sinon
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.readlines()
        
        modified = False
        
        for line_idx, orig_line in import_lines:
            # Remplacer SADIE par sadie
            new_line = orig_line.replace("SADIE", "sadie")
            
            if new_line != orig_line:
                modified = True
                if not dry_run:
                    content[line_idx] = new_line
        
        if modified and not dry_run:
            # Créer une sauvegarde avant modification
            backup_path = create_backup(file_path)
            
            # Écrire le fichier modifié
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(content)
            
            print(f"✅ Mis à jour: {file_path}")
            print(f"   Sauvegarde: {backup_path}")
        
        return modified
    
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour de {file_path}: {str(e)}")
        return False


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Migre les imports SADIE vers sadie (minuscules)"
    )
    parser.add_argument(
        "--dir", 
        default=".", 
        help="Répertoire racine à parcourir (défaut: répertoire courant)"
    )
    parser.add_argument(
        "--exclude", 
        default="old,.git,.venv,venv,__pycache__,build,dist", 
        help="Répertoires à exclure (séparés par des virgules)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Affiche les modifications sans les appliquer"
    )
    
    return parser.parse_args()


def main():
    """Fonction principale."""
    args = parse_arguments()
    
    print("=" * 80)
    print("🔄 MIGRATION DES IMPORTS SADIE → sadie")
    print("=" * 80)
    
    if args.dry_run:
        print("⚠️ Mode simulation: aucune modification ne sera effectuée")
    
    # Obtenir la liste des répertoires à exclure
    exclude_dirs = args.exclude.split(",")
    
    # Trouver tous les fichiers avec des imports SADIE
    files_with_imports = find_sadie_imports(args.dir, exclude_dirs)
    
    # Compter les imports à modifier
    total_import_lines = sum(len(lines) for _, lines in files_with_imports)
    
    if not files_with_imports:
        print("\n✅ Aucun fichier avec des imports 'SADIE' n'a été trouvé.")
        return
    
    print(f"\nTrouvé {len(files_with_imports)} fichiers avec {total_import_lines} imports 'SADIE':")
    
    for file_path, import_lines in files_with_imports:
        print(f"📄 {file_path} ({len(import_lines)} imports)")
        for line_idx, line in import_lines:
            print(f"   Ligne {line_idx + 1}: {line.strip()}")
    
    if not args.dry_run:
        print("\nMise à jour des imports...")
        
        # Créer le répertoire de sauvegarde si nécessaire
        os.makedirs("old/backups", exist_ok=True)
        
        # Mettre à jour les imports dans chaque fichier
        modified_count = 0
        for file_path, import_lines in files_with_imports:
            if update_imports(file_path, import_lines, args.dry_run):
                modified_count += 1
        
        print(f"\n✅ {modified_count} fichiers ont été mis à jour")
    else:
        print("\n⚠️ Mode simulation: aucune modification n'a été effectuée")
        print("   Pour appliquer les modifications, exécutez la commande sans --dry-run")


if __name__ == "__main__":
    main() 