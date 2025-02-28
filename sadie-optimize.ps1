#!/usr/bin/env pwsh
# SADIE - Script d'optimisation du système
# Ce script permet d'optimiser les performances du système SADIE

param (
    [string]$Action = "",
    [switch]$NonInteractive = $false,
    [string]$LogLevel = "Info", # Info, Warning, Error, Debug
    [string]$LogFile = "$PSScriptRoot\sadie-optimize.log"
)

# Définir l'encodage en UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Fonction de logging
function Write-Log {
    param (
        [string]$Message,
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Affichage en fonction du niveau de log
    switch ($Level) {
        "Info" {
            if ($LogLevel -in @("Info", "Debug")) {
                Write-Host $logEntry -ForegroundColor White
            }
        }
        "Warning" {
            if ($LogLevel -in @("Info", "Warning", "Debug")) {
                Write-Host $logEntry -ForegroundColor Yellow
            }
        }
        "Error" {
            if ($LogLevel -in @("Info", "Warning", "Error", "Debug")) {
                Write-Host $logEntry -ForegroundColor Red
            }
        }
        "Debug" {
            if ($LogLevel -eq "Debug") {
                Write-Host $logEntry -ForegroundColor Gray
            }
        }
    }
    
    # Écriture dans le fichier de log
    Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8
}

# Fonction pour afficher une bannière
function Show-Banner {
    Clear-Host
    $version = "1.0.0"
    
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                              ║" -ForegroundColor Cyan
    Write-Host "║                SADIE - SUITE D'OPTIMISATION                  ║" -ForegroundColor Cyan
    Write-Host "║                     Version $version                         ║" -ForegroundColor Cyan
    Write-Host "║                                                              ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

# Fonction pour afficher le menu principal
function Show-MainMenu {
    Write-Host "MENU PRINCIPAL" -ForegroundColor Yellow
    Write-Host "=============" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Diagnostic du système" -ForegroundColor White
    Write-Host "2. Optimisation du frontend" -ForegroundColor White
    Write-Host "3. Optimisation de la configuration réseau" -ForegroundColor White
    Write-Host "4. Gestion des conteneurs" -ForegroundColor White
    Write-Host "5. Maintenance du système" -ForegroundColor White
    Write-Host "6. Quitter" -ForegroundColor White
    Write-Host ""
}

# Fonction d'aide
function Show-Help {
    Write-Host "AIDE DU SCRIPT D'OPTIMISATION SADIE" -ForegroundColor Yellow
    Write-Host "==================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Usage: ./sadie-optimize.ps1 [-Action <action>] [-NonInteractive] [-LogLevel <level>] [-LogFile <path>]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Action <action>       : Action à exécuter (diagnostic, frontend, reseau, conteneurs, maintenance)"
    Write-Host "  -NonInteractive        : Exécute le script sans interactions utilisateur"
    Write-Host "  -LogLevel <level>      : Niveau de log (Info, Warning, Error, Debug)"
    Write-Host "  -LogFile <path>        : Chemin du fichier de log"
    Write-Host ""
    Write-Host "Exemples:"
    Write-Host "  ./sadie-optimize.ps1                          : Démarre le script en mode interactif"
    Write-Host "  ./sadie-optimize.ps1 -Action diagnostic       : Exécute le diagnostic du système"
    Write-Host "  ./sadie-optimize.ps1 -NonInteractive -Action maintenance : Exécute la maintenance sans interaction"
    Write-Host ""
}

# Fonction pour traiter les actions en ligne de commande
function Process-CommandLine {
    param (
        [string]$Action
    )
    
    switch ($Action.ToLower()) {
        "help" {
            Show-Help
            return $true
        }
        "diagnostic" {
            Write-Log "Exécution du diagnostic système..." -Level "Info"
            Run-Diagnostic
            return $true
        }
        "frontend" {
            Write-Log "Exécution de l'optimisation du frontend..." -Level "Info"
            Optimize-Frontend
            return $true
        }
        "reseau" {
            Write-Log "Exécution de l'optimisation réseau..." -Level "Info"
            Optimize-Network
            return $true
        }
        "conteneurs" {
            Write-Log "Gestion des conteneurs..." -Level "Info"
            Manage-Containers
            return $true
        }
        "maintenance" {
            Write-Log "Exécution de la maintenance système..." -Level "Info"
            System-Maintenance
            return $true
        }
        default {
            return $false
        }
    }
}

# Fonction de diagnostic
function Run-Diagnostic {
    Write-Log "Exécution du diagnostic système complet..." -Level "Info"
    try {
        & "$PSScriptRoot\diagnostic-sadie.ps1"
        Write-Log "Diagnostic terminé avec succès." -Level "Info"
    }
    catch {
        Write-Log "Erreur lors de l'exécution du diagnostic - $($_.Exception.Message)" -Level "Error"
    }
}

# Fonction d'optimisation du frontend
function Optimize-Frontend {
    Write-Log "Optimisation du frontend en cours..." -Level "Info"
    try {
        & "$PSScriptRoot\optimize-package-json.ps1"
        Write-Log "Optimisation du frontend terminée." -Level "Info"
    }
    catch {
        Write-Log "Erreur lors de l'optimisation du frontend - $($_.Exception.Message)" -Level "Error"
    }
}

# Fonction d'optimisation réseau
function Optimize-Network {
    Write-Log "Optimisation de la configuration réseau..." -Level "Info"
    try {
        & "$PSScriptRoot\optimize-network.ps1"
        Write-Log "Optimisation réseau terminée." -Level "Info"
    }
    catch {
        Write-Log "Erreur lors de l'optimisation réseau - $($_.Exception.Message)" -Level "Error"
    }
}

# Fonction de gestion des conteneurs
function Manage-Containers {
    Write-Host "GESTION DES CONTENEURS" -ForegroundColor Yellow
    Write-Host "====================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Redémarrer tous les conteneurs" -ForegroundColor White
    Write-Host "2. Redémarrer uniquement le frontend" -ForegroundColor White
    Write-Host "3. Nettoyer les conteneurs inutilisés" -ForegroundColor White
    Write-Host "4. Vérifier le réseau des conteneurs" -ForegroundColor White
    Write-Host "5. Retour" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Choisissez une option"
    
    switch ($choice) {
        "1" {
            Write-Log "Redémarrage de tous les conteneurs..." -Level "Info"
            & "$PSScriptRoot\restart-containers.ps1"
        }
        "2" {
            Write-Log "Redémarrage du frontend..." -Level "Info"
            & "$PSScriptRoot\restart-sadie-frontend.ps1"
        }
        "3" {
            Write-Log "Nettoyage des conteneurs..." -Level "Info"
            & "$PSScriptRoot\clean-docker.ps1"
        }
        "4" {
            Write-Log "Vérification du réseau des conteneurs..." -Level "Info"
            & "$PSScriptRoot\check-docker-network.ps1"
        }
        "5" {
            return
        }
        default {
            Write-Log "Option invalide. Veuillez réessayer." -Level "Warning"
            Manage-Containers
        }
    }
}

# Fonction de maintenance système
function System-Maintenance {
    Write-Host "MAINTENANCE DU SYSTÈME" -ForegroundColor Yellow
    Write-Host "====================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Optimisation du système complet" -ForegroundColor White
    Write-Host "2. Vérification des mises à jour" -ForegroundColor White
    Write-Host "3. Backup des configurations" -ForegroundColor White
    Write-Host "4. Retour" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Choisissez une option"
    
    switch ($choice) {
        "1" {
            Write-Log "Optimisation du système complet..." -Level "Info"
            & "$PSScriptRoot\optimize-sadie-system.ps1"
        }
        "2" {
            Write-Log "Vérification des mises à jour..." -Level "Info"
            Write-Log "Fonctionnalité à implémenter" -Level "Warning"
        }
        "3" {
            Write-Log "Backup des configurations..." -Level "Info"
            Write-Log "Fonctionnalité à implémenter" -Level "Warning"
        }
        "4" {
            return
        }
        default {
            Write-Log "Option invalide. Veuillez réessayer." -Level "Warning"
            System-Maintenance
        }
    }
}

# Point d'entrée principal du script
try {
    # Vérifier si une action est fournie en ligne de commande
    if ($NonInteractive -or $Action -ne "") {
        $actionProcessed = Process-CommandLine -Action $Action
        # Si l'action a été traitée ou si le mode non-interactif est activé, on termine
        if ($actionProcessed -or $NonInteractive) {
            exit 0
        }
    }
    
    # Mode interactif
    Show-Banner
    
    do {
        Show-MainMenu
        $choice = Read-Host "Choisissez une option"
        
        switch ($choice) {
            "1" {
                Run-Diagnostic
            }
            "2" {
                Optimize-Frontend
            }
            "3" {
                Optimize-Network
            }
            "4" {
                Manage-Containers
            }
            "5" {
                System-Maintenance
            }
            "6" {
                Write-Log "Fin du script." -Level "Info"
                exit 0
            }
            default {
                Write-Log "Option invalide. Veuillez réessayer." -Level "Warning"
            }
        }
        
        Write-Host "`nAppuyez sur une touche pour continuer..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Clear-Host
        Show-Banner
    } while ($true)
}
catch {
    $scriptName = $MyInvocation.MyCommand.Name
    Write-Log "Erreur lors de l'exécution de $scriptName - $($_.Exception.Message)" -Level "Error"
    exit 1
} 