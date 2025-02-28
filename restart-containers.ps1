!/usr/bin/env pwsh

# Script pour redÃ©marrer les conteneurs SADIE avec des configurations optimisÃ©es
Write-Host "Gestion des conteneurs SADIE..." -ForegroundColor Cyan

# VÃ©rifier si Docker est en cours d'exÃ©cution
try {
    $dockerStatus = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur: Docker n'est pas en cours d'exÃ©cution. Veuillez dÃ©marrer Docker Desktop." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Erreur: Docker n'est pas installÃ© ou n'est pas accessible. Veuillez installer Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "Docker est en cours d'exÃ©cution." -ForegroundColor Green

# VÃ©rifier les conteneurs SADIE existants
$sadieContainers = docker ps -a --filter "name=sadie" --format "{{.Names}}"
Write-Host "`nConteneurs SADIE existants:" -ForegroundColor Yellow
if ($sadieContainers) {
    $sadieContainers | ForEach-Object { Write-Host "- $_" }
} else {
    Write-Host "Aucun conteneur SADIE trouvÃ©." -ForegroundColor Yellow
}

# VÃ©rifier si docker-compose.yml existe
$dockerComposeExists = Test-Path "docker-compose.yml"
if (-not $dockerComposeExists) {
    $dockerComposeExists = Test-Path "frontend/docker-compose.yml"
    if ($dockerComposeExists) {
        $dockerComposePath = "frontend/docker-compose.yml"
    }
} else {
    $dockerComposePath = "docker-compose.yml"
}

# Fonction pour redÃ©marrer un conteneur spÃ©cifique
function Restart-Container {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ContainerName
    )
    
    Write-Host "`nGestion du conteneur $ContainerName..." -ForegroundColor Cyan
    
    # VÃ©rifier si le conteneur existe
    $containerExists = docker ps -a --filter "name=$ContainerName" --format "{{.Names}}"
    
    if ($containerExists) {
        # ArrÃªter le conteneur s'il est en cours d'exÃ©cution
        $containerRunning = docker ps --filter "name=$ContainerName" --format "{{.Names}}"
        if ($containerRunning) {
            Write-Host "ArrÃªt du conteneur $ContainerName..." -ForegroundColor Yellow
            docker stop $ContainerName
        }
        
        # Supprimer le conteneur
        Write-Host "Suppression du conteneur $ContainerName..." -ForegroundColor Yellow
        docker rm $ContainerName
    } else {
        Write-Host "Le conteneur $ContainerName n'existe pas encore." -ForegroundColor Yellow
    }
    
    # Reconstruire et dÃ©marrer le conteneur
    if ($dockerComposeExists) {
        Write-Host "Utilisation de docker-compose ($dockerComposePath) pour redÃ©marrer $ContainerName..." -ForegroundColor Green
        
        if ($ContainerName -eq "sadie-frontend") {
            # Application des optimisations avant de dÃ©marrer
            Write-Host "Application des optimisations pour le frontend..." -ForegroundColor Yellow
            
            # ExÃ©cuter le script d'optimisation du package.json s'il existe
            if (Test-Path "optimize-package-json.ps1") {
                Write-Host "ExÃ©cution du script d'optimisation du package.json..." -ForegroundColor Yellow
                ./optimize-package-json.ps1
            }
            
            # ExÃ©cuter le script d'optimisation du Dockerfile s'il existe
            if (Test-Path "optimize-dockerfile.ps1") {
                Write-Host "ExÃ©cution du script d'optimisation du Dockerfile..." -ForegroundColor Yellow
                ./optimize-dockerfile.ps1
            }
            
            # RedÃ©marrer avec docker-compose
            if ($dockerComposePath -eq "docker-compose.yml") {
                docker-compose build frontend
                docker-compose up -d frontend
            } else {
                # Si le fichier docker-compose.yml est dans un sous-dossier
                Set-Location -Path (Split-Path -Parent $dockerComposePath)
                docker-compose build frontend
                docker-compose up -d frontend
                Set-Location -Path ".."
            }
        } else {
            # Pour les autres conteneurs
            if ($dockerComposePath -eq "docker-compose.yml") {
                docker-compose up -d $ContainerName
            } else {
                # Si le fichier docker-compose.yml est dans un sous-dossier
                Set-Location -Path (Split-Path -Parent $dockerComposePath)
                docker-compose up -d $ContainerName
                Set-Location -Path ".."
            }
        }
    } else {
        Write-Host "Aucun fichier docker-compose.yml trouvÃ©." -ForegroundColor Red
        
        if ($ContainerName -eq "sadie-frontend") {
            # DÃ©marrer le conteneur frontend manuellement
            Write-Host "DÃ©marrage manuel du conteneur $ContainerName..." -ForegroundColor Yellow
            
            # VÃ©rifier si le script d'optimisation du Dockerfile a Ã©tÃ© exÃ©cutÃ©
            if (Test-Path "frontend/Dockerfile") {
                Write-Host "Construction de l'image frontend..." -ForegroundColor Yellow
                docker build -t sadie-frontend:latest ./frontend
                
                Write-Host "DÃ©marrage du conteneur frontend..." -ForegroundColor Green
                docker run -d --name sadie-frontend -p 3000:3000 -e NODE_OPTIONS=--max-old-space-size=4096 sadie-frontend:latest
            } else {
                Write-Host "Erreur: Dockerfile du frontend introuvable." -ForegroundColor Red
                Write-Host "Veuillez exÃ©cuter le script optimize-dockerfile.ps1 pour crÃ©er le Dockerfile optimisÃ©." -ForegroundColor Yellow
            }
        } else {
            Write-Host "DÃ©marrage manuel du conteneur $ContainerName non pris en charge." -ForegroundColor Red
            Write-Host "Veuillez crÃ©er un fichier docker-compose.yml ou dÃ©marrer manuellement le conteneur." -ForegroundColor Yellow
        }
    }
    
    # VÃ©rifier si le conteneur est maintenant en cours d'exÃ©cution
    Start-Sleep -Seconds 2
    $containerRunning = docker ps --filter "name=$ContainerName" --format "{{.Names}}"
    
    if ($containerRunning) {
        Write-Host "Le conteneur $ContainerName a Ã©tÃ© redÃ©marrÃ© avec succÃ¨s." -ForegroundColor Green
        
        if ($ContainerName -eq "sadie-frontend") {
            # Afficher les logs du frontend pour vÃ©rifier le dÃ©marrage
            Write-Host "`nLogs du frontend (30 derniÃ¨res lignes):" -ForegroundColor Yellow
            docker logs sadie-frontend --tail 30
            
            # VÃ©rifier l'Ã©tat du serveur frontend
            $frontendLogs = docker logs sadie-frontend --tail 30
            if ($frontendLogs -match "Compiled successfully") {
                Write-Host "`nLe serveur frontend a dÃ©marrÃ© avec succÃ¨s!" -ForegroundColor Green
                Write-Host "AccÃ©dez Ã  http://localhost:3000 pour voir l'application." -ForegroundColor Cyan
            } elseif ($frontendLogs -match "Starting the development server") {
                Write-Host "`nLe serveur frontend est en cours de dÃ©marrage..." -ForegroundColor Yellow
                Write-Host "VÃ©rifiez l'Ã©tat dans quelques instants avec: docker logs sadie-frontend --tail 10" -ForegroundColor Yellow
            } else {
                Write-Host "`nProblÃ¨me dÃ©tectÃ© lors du dÃ©marrage!" -ForegroundColor Red
                Write-Host "VÃ©rifiez les logs complets avec: docker logs sadie-frontend" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "Erreur: Le conteneur $ContainerName n'a pas pu Ãªtre dÃ©marrÃ©." -ForegroundColor Red
    }
}

# Menu pour choisir l'action
Write-Host "`nQue souhaitez-vous faire?" -ForegroundColor Cyan
Write-Host "1. RedÃ©marrer uniquement le frontend"
Write-Host "2. RedÃ©marrer tous les conteneurs SADIE"
Write-Host "3. Afficher les logs du frontend"
Write-Host "4. Quitter"

$choice = Read-Host "Entrez votre choix"

switch ($choice) {
    "1" {
        Restart-Container -ContainerName "sadie-frontend"
    }
    "2" {
        if ($sadieContainers) {
            $sadieContainers | ForEach-Object { Restart-Container -ContainerName $_ }
        } else {
            Write-Host "Aucun conteneur SADIE trouvÃ© Ã  redÃ©marrer." -ForegroundColor Yellow
            Restart-Container -ContainerName "sadie-frontend"
        }
    }
    "3" {
        Write-Host "`nLogs du frontend:" -ForegroundColor Yellow
        docker logs sadie-frontend --tail 50
    }
    "4" {
        Write-Host "Au revoir!" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "Choix invalide. RedÃ©marrage uniquement du frontend." -ForegroundColor Yellow
        Restart-Container -ContainerName "sadie-frontend"
    }
}

Write-Host "`nGestion des conteneurs SADIE terminÃ©e!" -ForegroundColor Green 