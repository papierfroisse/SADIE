#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de validation des dépendances du projet sadie.
Ce script vérifie que toutes les dépendances nécessaires sont installées
et que leurs versions sont compatibles avec celles spécifiées dans requirements.txt.
"""

import sys
import subprocess
import re
import pkg_resources
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional


def get_installed_packages() -> Dict[str, str]:
    """
    Obtient la liste des packages installés et leurs versions.
    
    Returns:
        Dict[str, str]: Un dictionnaire {nom_package: version}
    """
    installed_packages = {}
    
    for package in pkg_resources.working_set:
        name = package.project_name.lower()
        version = package.version
        installed_packages[name] = version
    
    return installed_packages


def parse_requirements_file(file_path: str) -> Dict[str, str]:
    """
    Parse un fichier requirements.txt pour extraire les packages et leurs contraintes de version.
    
    Args:
        file_path (str): Chemin vers le fichier requirements.txt
        
    Returns:
        Dict[str, str]: Un dictionnaire {nom_package: contrainte_version}
    """
    requirements = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Ignorer les commentaires et les lignes vides
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Gérer les options comme -r ou -e
                if line.startswith('-'):
                    continue
                
                # Extraire le nom et la contrainte de version
                if ';' in line:  # Ignorer les markers de plateforme
                    line = line.split(';')[0].strip()
                
                # Traiter les dépendances Git et autres URL
                if "git+" in line or "http://" in line or "https://" in line:
                    if "#egg=" in line:
                        package = line.split("#egg=")[1].split("&")[0].split("-")[0].lower()
                        requirements[package] = "URL"
                    continue
                
                # Format standard: package==version ou package>=version, etc.
                match = re.match(r'^([a-zA-Z0-9_\-]+)(.*)$', line)
                if match:
                    package_name = match.group(1).lower()
                    version_constraint = match.group(2).strip()
                    requirements[package_name] = version_constraint
    
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier {file_path}: {str(e)}")
        return {}
    
    return requirements


def check_version_compatibility(
    package: str, 
    installed_version: str, 
    required_constraint: str
) -> bool:
    """
    Vérifie si la version installée est compatible avec la contrainte requise.
    
    Args:
        package (str): Nom du package
        installed_version (str): Version installée
        required_constraint (str): Contrainte de version requise
        
    Returns:
        bool: True si compatible, False sinon
    """
    # Si pas de contrainte ou URL, on considère comme compatible
    if not required_constraint or required_constraint == "URL":
        return True
    
    try:
        # Créer un objet de spécification à partir de la contrainte
        spec = f"{package}{required_constraint}"
        requirement = pkg_resources.Requirement.parse(spec)
        
        # Vérifier si la version installée satisfait la spécification
        return pkg_resources.parse_version(installed_version) in requirement
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification de compatibilité pour {package}: {str(e)}")
        # En cas d'erreur, on considère comme compatible pour éviter les faux positifs
        return True


def validate_dependencies(requirements_file: str = "requirements.txt") -> Tuple[int, int, List[str]]:
    """
    Valide que toutes les dépendances nécessaires sont installées avec des versions compatibles.
    
    Args:
        requirements_file (str): Chemin vers le fichier requirements.txt
        
    Returns:
        Tuple[int, int, List[str]]: (nombre_ok, nombre_problèmes, liste_problèmes)
    """
    # Vérifier que le fichier requirements.txt existe
    if not Path(requirements_file).exists():
        return 0, 1, [f"❌ Le fichier {requirements_file} n'existe pas"]
    
    # Obtenir les packages installés
    installed_packages = get_installed_packages()
    
    # Parser le fichier requirements.txt
    required_packages = parse_requirements_file(requirements_file)
    
    if not required_packages:
        return 0, 1, [f"❌ Le fichier {requirements_file} est vide ou mal formaté"]
    
    issues = []
    ok_count = 0
    
    # Vérifier que chaque package requis est installé avec une version compatible
    for package, constraint in required_packages.items():
        if package in installed_packages:
            installed_version = installed_packages[package]
            if check_version_compatibility(package, installed_version, constraint):
                ok_count += 1
            else:
                issues.append(
                    f"⚠️ Version incompatible pour {package}: "
                    f"installé={installed_version}, requis={constraint}"
                )
        else:
            # Certains packages peuvent être installés sous un nom différent
            # ou faire partie de packages plus grands
            issues.append(f"❓ Package non trouvé: {package}{constraint}")
    
    return ok_count, len(issues), issues


def main():
    """Fonction principale."""
    requirements_file = "requirements.txt"
    
    if len(sys.argv) > 1:
        requirements_file = sys.argv[1]
    
    print("=" * 80)
    print(f"🔍 VALIDATION DES DÉPENDANCES ({requirements_file})")
    print("=" * 80)
    
    ok_count, issues_count, issues = validate_dependencies(requirements_file)
    
    # Afficher les résultats
    if issues_count == 0:
        print(f"✅ Toutes les dépendances ({ok_count}) sont correctement installées.")
    else:
        print(f"⚠️ {ok_count} dépendances sont correctement installées, mais {issues_count} problèmes ont été détectés:")
        for issue in issues:
            print(f"  {issue}")
    
    # S'il y a des problèmes graves (packages manquants), sortir avec un code d'erreur
    missing_packages = [i for i in issues if "❓ Package non trouvé" in i]
    if missing_packages:
        print(f"\n❌ {len(missing_packages)} packages requis ne sont pas installés.")
        print("   Pour installer toutes les dépendances manquantes, exécutez:")
        print(f"   pip install -r {requirements_file}")
        sys.exit(1)
    
    # S'il y a des problèmes de version uniquement, sortir avec un avertissement
    if issues_count > 0:
        print("\n⚠️ Certaines versions de packages ne correspondent pas aux exigences.")
        print("   Pour mettre à jour les dépendances, exécutez:")
        print(f"   pip install -r {requirements_file} --upgrade")
        sys.exit(0)
    
    sys.exit(0)


if __name__ == "__main__":
    main() 