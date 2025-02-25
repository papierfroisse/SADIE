#!/usr/bin/env python
"""
Script de sauvegarde automatique pour le projet SADIE.

Ce script effectue une sauvegarde complète des données du projet,
incluant la base de données, les fichiers de configuration et les logs.
Il prend en charge la rotation des sauvegardes et la compression.
"""

import argparse
import datetime
import logging
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import dotenv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/backup.log"),
    ],
)
logger = logging.getLogger("sadie.backup")

# Chargement des variables d'environnement
dotenv.load_dotenv()

# Valeurs par défaut
DEFAULT_BACKUP_DIR = os.getenv("BACKUP_STORAGE_PATH", "./backups")
DEFAULT_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", 30))


def parse_arguments():
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description="Script de sauvegarde pour SADIE")
    parser.add_argument(
        "--backup-dir",
        type=str,
        default=DEFAULT_BACKUP_DIR,
        help="Répertoire de destination des sauvegardes",
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=DEFAULT_RETENTION_DAYS,
        help="Nombre de jours de conservation des sauvegardes",
    )
    parser.add_argument(
        "--db-only",
        action="store_true",
        help="Sauvegarder uniquement la base de données",
    )
    parser.add_argument(
        "--no-compression",
        action="store_true",
        help="Désactiver la compression des sauvegardes",
    )
    return parser.parse_args()


def create_backup_dir(backup_dir):
    """Crée le répertoire de sauvegarde s'il n'existe pas."""
    try:
        os.makedirs(backup_dir, exist_ok=True)
        logger.info(f"Répertoire de sauvegarde: {backup_dir}")
    except Exception as e:
        logger.error(f"Impossible de créer le répertoire de sauvegarde: {e}")
        sys.exit(1)


def backup_database(backup_dir, timestamp):
    """Sauvegarde la base de données PostgreSQL."""
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "sadie")
    db_user = os.getenv("DB_USER", "postgres")
    
    backup_file = os.path.join(backup_dir, f"sadie_db_{timestamp}.sql")
    
    try:
        # Construction de la commande pg_dump
        cmd = [
            "pg_dump",
            f"--host={db_host}",
            f"--port={db_port}",
            f"--username={db_user}",
            f"--dbname={db_name}",
            f"--file={backup_file}",
            "--format=plain",
            "--schema=public",
        ]
        
        # Exécution de pg_dump
        logger.info(f"Sauvegarde de la base de données vers {backup_file}")
        subprocess.run(cmd, check=True, capture_output=True, env={
            **os.environ,
            "PGPASSWORD": os.getenv("DB_PASSWORD", ""),
        })
        
        logger.info("Sauvegarde de la base de données réussie")
        return backup_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la sauvegarde de la base de données: {e.stderr.decode()}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la sauvegarde de la base de données: {e}")
        return None


def backup_files(backup_dir, timestamp):
    """Sauvegarde les fichiers importants du projet."""
    files_to_backup = [
        ".env",
        "config/",
        "logs/",
        "data/",
    ]
    
    backup_folder = os.path.join(backup_dir, f"sadie_files_{timestamp}")
    
    try:
        os.makedirs(backup_folder, exist_ok=True)
        
        for file_path in files_to_backup:
            dest = os.path.join(backup_folder, os.path.basename(file_path.rstrip("/")))
            src = file_path
            
            if os.path.isdir(src):
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dest)
        
        logger.info(f"Sauvegarde des fichiers réussie dans {backup_folder}")
        return backup_folder
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des fichiers: {e}")
        return None


def compress_backup(backup_dir, timestamp, files_to_compress):
    """Compresse les fichiers de sauvegarde en une archive tar.gz."""
    archive_name = os.path.join(backup_dir, f"sadie_backup_{timestamp}.tar.gz")
    
    try:
        with tarfile.open(archive_name, "w:gz") as tar:
            for file_path in files_to_compress:
                if file_path and os.path.exists(file_path):
                    arcname = os.path.basename(file_path)
                    tar.add(file_path, arcname=arcname)
        
        logger.info(f"Compression des sauvegardes réussie: {archive_name}")
        
        # Suppression des fichiers originaux après compression
        for file_path in files_to_compress:
            if file_path and os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
        
        return archive_name
    except Exception as e:
        logger.error(f"Erreur lors de la compression des sauvegardes: {e}")
        return None


def cleanup_old_backups(backup_dir, retention_days):
    """Supprime les sauvegardes plus anciennes que retention_days."""
    try:
        now = datetime.datetime.now()
        retention_date = now - datetime.timedelta(days=retention_days)
        
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            
            # Ignorer les dossiers et fichiers non-sauvegardes
            if not os.path.isfile(item_path) or not item.startswith("sadie_backup_"):
                continue
            
            # Extraction de la date à partir du nom de fichier
            try:
                # Format: sadie_backup_YYYYMMDD_HHMMSS.tar.gz
                date_str = item.split("_")[2].split(".")[0]
                date = datetime.datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                
                if date < retention_date:
                    os.remove(item_path)
                    logger.info(f"Suppression de l'ancienne sauvegarde: {item}")
            except (IndexError, ValueError):
                logger.warning(f"Format de nom de sauvegarde non reconnu: {item}")
                continue
        
        logger.info(f"Nettoyage des sauvegardes terminé (rétention: {retention_days} jours)")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des anciennes sauvegardes: {e}")


def main():
    """Fonction principale du script de sauvegarde."""
    args = parse_arguments()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger.info(f"Démarrage de la sauvegarde SADIE ({timestamp})")
    
    # Création du répertoire de sauvegarde
    create_backup_dir(args.backup_dir)
    
    files_to_compress = []
    
    # Sauvegarde de la base de données
    db_backup = backup_database(args.backup_dir, timestamp)
    if db_backup:
        files_to_compress.append(db_backup)
    
    # Sauvegarde des fichiers si demandé
    if not args.db_only:
        files_backup = backup_files(args.backup_dir, timestamp)
        if files_backup:
            files_to_compress.append(files_backup)
    
    # Compression des sauvegardes
    if not args.no_compression and files_to_compress:
        compress_backup(args.backup_dir, timestamp, files_to_compress)
    
    # Nettoyage des anciennes sauvegardes
    cleanup_old_backups(args.backup_dir, args.retention_days)
    
    logger.info("Sauvegarde terminée avec succès")


if __name__ == "__main__":
    main() 