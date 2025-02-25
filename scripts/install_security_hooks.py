#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour installer les hooks de sécurité Git pour le projet sadie.
Ce script installe un hook de pre-commit qui exécute les vérifications de sécurité
avant chaque commit.
"""

import os
import sys
import stat
from pathlib import Path


def install_pre_commit_hook():
    """Installe le hook de pre-commit."""
    git_dir = Path(".git")
    hooks_dir = git_dir / "hooks"
    
    if not git_dir.exists():
        print("❌ Répertoire .git non trouvé. Êtes-vous dans un dépôt Git?")
        return False
    
    if not hooks_dir.exists():
        print(f"📁 Création du répertoire {hooks_dir}")
        hooks_dir.mkdir(exist_ok=True)
    
    pre_commit_path = hooks_dir / "pre-commit"
    
    # Contenu du hook pre-commit
    hook_content = """#!/bin/sh
# Hook de pre-commit pour vérifications de sécurité sadie

echo "🔒 Exécution des vérifications de sécurité..."
python scripts/security_check.py

if [ $? -ne 0 ]; then
    echo "❌ Les vérifications de sécurité ont échoué. Commit abandonné."
    echo "   Consultez les messages ci-dessus pour plus de détails."
    echo "   Pour ignorer ces vérifications (déconseillé), utilisez l'option --no-verify"
    exit 1
fi

echo "✅ Vérifications de sécurité réussies."
"""
    
    # Écrire le hook
    with open(pre_commit_path, 'w') as f:
        f.write(hook_content)
    
    # Rendre le script exécutable
    os.chmod(pre_commit_path, os.stat(pre_commit_path).st_mode | stat.S_IEXEC)
    
    print(f"✅ Hook pre-commit installé avec succès dans {pre_commit_path}")
    return True


def main():
    """Fonction principale pour installer les hooks de sécurité."""
    print("🔧 Installation des hooks de sécurité Git pour sadie...")
    
    success = install_pre_commit_hook()
    
    if success:
        print("\n✅ Installation des hooks de sécurité terminée avec succès.")
        print("   Les vérifications de sécurité seront exécutées automatiquement avant chaque commit.")
    else:
        print("\n❌ L'installation des hooks de sécurité a échoué.")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main() 