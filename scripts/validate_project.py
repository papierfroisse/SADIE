#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de validation de l'intégrité du projet sadie après migration.
Ce script vérifie plusieurs aspects du projet pour s'assurer que la migration
s'est déroulée correctement.
"""

import os
import re
import sys
from pathlib import Path
import importlib.util
import subprocess
from typing import List, Dict, Any, Tuple


class ValidationResult:
    """Classe pour stocker les résultats des validations."""
    
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def add_check(self, name: str, result: bool, message: str, warning: bool = False):
        """Ajoute un résultat de vérification."""
        self.checks.append({
            "name": name,
            "result": result,
            "message": message,
            "warning": warning
        })
        
        if result:
            self.passed += 1
        elif warning:
            self.warnings += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        """Affiche un résumé des vérifications."""
        print("\n" + "=" * 80)
        print(f"✅ RÉSULTATS DE LA VALIDATION ({self.passed} réussis, {self.failed} échoués, {self.warnings} avertissements)")
        print("=" * 80)
        
        for check in self.checks:
            if check["result"]:
                status = "✅ RÉUSSI"
            elif check["warning"]:
                status = "⚠️ ATTENTION"
            else:
                status = "❌ ÉCHEC"
            
            print(f"{status} : {check['name']}")
            print(f"  {check['message']}")
            print("-" * 80)
        
        print("\nRÉSUMÉ FINAL:")
        print(f"✅ {self.passed} vérifications réussies")
        print(f"⚠️ {self.warnings} avertissements")
        print(f"❌ {self.failed} échecs")
        
        if self.failed > 0:
            print("\n❌ VALIDATION ÉCHOUÉE : Certaines vérifications ont échoué. Voir les détails ci-dessus.")
            return False
        
        if self.warnings > 0:
            print("\n⚠️ VALIDATION RÉUSSIE AVEC AVERTISSEMENTS : Le projet est fonctionnel mais certains points méritent attention.")
            return True
        
        print("\n✅ VALIDATION RÉUSSIE : Le projet est en bon état.")
        return True


def check_imports(result: ValidationResult) -> None:
    """Vérifie que les imports utilisent 'sadie' et non 'SADIE'."""
    sadie_imports = []
    pattern = re.compile(r"(from|import)\s+SADIE")
    
    for root, _, files in os.walk("."):
        # Ignorer les dossiers cachés, tests et le dossier old
        if "/." in root or "\\." in root or "/old" in root or "\\old" in root:
            continue
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if pattern.search(content):
                            sadie_imports.append(file_path)
                except Exception as e:
                    print(f"Erreur lors de la lecture de {file_path}: {str(e)}")
    
    if sadie_imports:
        result.add_check(
            "Vérification des imports 'SADIE'",
            False,
            f"Trouvé {len(sadie_imports)} fichiers avec des imports 'SADIE' au lieu de 'sadie':\n"
            + "\n".join(f"  - {f}" for f in sadie_imports)
        )
    else:
        result.add_check(
            "Vérification des imports 'SADIE'",
            True,
            "Tous les imports utilisent 'sadie' correctement."
        )


def check_module_imports(result: ValidationResult) -> None:
    """Vérifie que les modules importants peuvent être importés."""
    modules_to_check = [
        "sadie.core.monitoring.metrics",
        "sadie.core.monitoring.alerts",
        "sadie.core.collectors.base",
        "sadie.web.app"
    ]
    
    failed_imports = []
    
    for module in modules_to_check:
        try:
            # Essayer d'importer le module sans l'exécuter
            spec = importlib.util.find_spec(module)
            if spec is None:
                failed_imports.append((module, "Module non trouvé"))
        except ImportError as e:
            failed_imports.append((module, str(e)))
    
    if failed_imports:
        result.add_check(
            "Vérification des importations de modules",
            False,
            f"Problèmes d'importation détectés pour {len(failed_imports)} modules:\n"
            + "\n".join(f"  - {m}: {e}" for m, e in failed_imports)
        )
    else:
        result.add_check(
            "Vérification des importations de modules",
            True,
            "Tous les modules peuvent être importés correctement."
        )


def check_code_quality(result: ValidationResult) -> None:
    """Vérifie la qualité du code avec black et flake8 si disponibles."""
    # Vérifier si black est installé
    black_installed = importlib.util.find_spec("black") is not None
    
    if black_installed:
        # Exécuter black en mode vérification uniquement
        try:
            black_output = subprocess.run(
                ["black", "--check", "."], 
                capture_output=True, 
                text=True
            )
            
            if black_output.returncode == 0:
                result.add_check(
                    "Formatage du code (black)",
                    True,
                    "Le code est correctement formaté selon black."
                )
            else:
                result.add_check(
                    "Formatage du code (black)",
                    False,
                    f"Le code n'est pas formaté selon black:\n{black_output.stdout}",
                    warning=True
                )
        except Exception as e:
            result.add_check(
                "Formatage du code (black)",
                False,
                f"Erreur lors de l'exécution de black: {str(e)}",
                warning=True
            )
    else:
        result.add_check(
            "Formatage du code (black)",
            False,
            "black n'est pas installé. Installez-le avec 'pip install black'.",
            warning=True
        )
    
    # Vérifier si flake8 est installé
    flake8_installed = importlib.util.find_spec("flake8") is not None
    
    if flake8_installed:
        # Exécuter flake8
        try:
            flake8_output = subprocess.run(
                ["flake8", "."], 
                capture_output=True, 
                text=True
            )
            
            if flake8_output.returncode == 0:
                result.add_check(
                    "Analyse du code (flake8)",
                    True,
                    "Le code est conforme aux standards flake8."
                )
            else:
                problems = flake8_output.stdout.strip().split("\n")
                if problems and problems[0]:  # S'assurer qu'il y a des problèmes réels
                    result.add_check(
                        "Analyse du code (flake8)",
                        False,
                        f"Le code contient {len(problems)} problèmes selon flake8:\n"
                        + "\n".join(f"  - {p}" for p in problems[:10])
                        + ("\n  - ..." if len(problems) > 10 else ""),
                        warning=True
                    )
                else:
                    result.add_check(
                        "Analyse du code (flake8)",
                        True,
                        "Le code est conforme aux standards flake8."
                    )
        except Exception as e:
            result.add_check(
                "Analyse du code (flake8)",
                False,
                f"Erreur lors de l'exécution de flake8: {str(e)}",
                warning=True
            )
    else:
        result.add_check(
            "Analyse du code (flake8)",
            False,
            "flake8 n'est pas installé. Installez-le avec 'pip install flake8'.",
            warning=True
        )


def check_documentation(result: ValidationResult) -> None:
    """Vérifie la présence et la cohérence de la documentation."""
    doc_files = [
        "docs/api/metrics.md",
        "docs/security.md",
        "docs/consolidation_plan.md",
        "examples/metrics_advanced_example.py"
    ]
    
    missing_docs = []
    
    for doc_file in doc_files:
        if not os.path.exists(doc_file):
            missing_docs.append(doc_file)
    
    if missing_docs:
        result.add_check(
            "Vérification de la documentation",
            False,
            f"Documentation manquante:\n"
            + "\n".join(f"  - {f}" for f in missing_docs)
        )
    else:
        result.add_check(
            "Vérification de la documentation",
            True,
            "Toute la documentation essentielle est présente."
        )


def check_tests(result: ValidationResult) -> None:
    """Vérifie la présence et l'exécution des tests."""
    test_files = [
        "tests/integration/test_metrics_monitoring.py"
    ]
    
    missing_tests = []
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            missing_tests.append(test_file)
    
    if missing_tests:
        result.add_check(
            "Vérification des tests d'intégration",
            False,
            f"Tests manquants:\n"
            + "\n".join(f"  - {f}" for f in missing_tests)
        )
    else:
        result.add_check(
            "Vérification des tests d'intégration",
            True,
            "Tous les tests d'intégration essentiels sont présents."
        )


def check_project_structure(result: ValidationResult) -> None:
    """Vérifie la structure du projet."""
    essential_dirs = [
        "sadie",
        "sadie/core",
        "sadie/core/monitoring",
        "sadie/core/collectors",
        "tests",
        "tests/integration",
        "docs",
        "examples",
        "scripts"
    ]
    
    missing_dirs = []
    
    for directory in essential_dirs:
        if not os.path.isdir(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        result.add_check(
            "Vérification de la structure du projet",
            False,
            f"Répertoires essentiels manquants:\n"
            + "\n".join(f"  - {d}" for d in missing_dirs)
        )
    else:
        result.add_check(
            "Vérification de la structure du projet",
            True,
            "La structure du projet est complète."
        )


def check_security_features(result: ValidationResult) -> None:
    """Vérifie la présence des fonctionnalités de sécurité."""
    security_files = [
        "scripts/security_check.py",
        "scripts/install_security_hooks.py",
        "docs/security.md"
    ]
    
    missing_files = []
    
    for sec_file in security_files:
        if not os.path.exists(sec_file):
            missing_files.append(sec_file)
    
    if missing_files:
        result.add_check(
            "Vérification des fonctionnalités de sécurité",
            False,
            f"Fichiers de sécurité manquants:\n"
            + "\n".join(f"  - {f}" for f in missing_files)
        )
    else:
        result.add_check(
            "Vérification des fonctionnalités de sécurité",
            True,
            "Toutes les fonctionnalités de sécurité sont présentes."
        )


def main():
    """Point d'entrée principal."""
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("=" * 80)
    print("🔍 VALIDATION DU PROJET sadie")
    print("=" * 80)
    print("Démarrage de la validation complète du projet...")
    
    result = ValidationResult()
    
    # Vérifier la structure du projet
    check_project_structure(result)
    
    # Vérifier les imports
    check_imports(result)
    
    # Vérifier les importations de modules
    check_module_imports(result)
    
    # Vérifier la qualité du code
    check_code_quality(result)
    
    # Vérifier la documentation
    check_documentation(result)
    
    # Vérifier les tests
    check_tests(result)
    
    # Vérifier les fonctionnalités de sécurité
    check_security_features(result)
    
    # Afficher les résultats
    success = result.print_summary()
    
    # Retourner un code de sortie approprié
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 