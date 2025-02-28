!/usr/bin/env pwsh

# SADIE - Suite d'optimisation unifiÃ©e (Version simplifiÃ©e)
# ====================================

function Show-Banner {
    Clear-Host
    $version = "1.0.0"
    
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "           SADIE - SUITE D'OPTIMISATION              " -ForegroundColor Cyan
    Write-Host "                 Version $version                    " -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Show-MainMenu {
    Write-Host "MENU PRINCIPAL" -ForegroundColor Yellow
    Write-Host "=============" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Optimiser le Dockerfile" -ForegroundColor White
    Write-Host "2. RedÃ©marrer les conteneurs" -ForegroundColor White
    Write-Host "3. Nettoyer Docker" -ForegroundColor White
    Write-Host "4. Quitter" -ForegroundColor White
    Write-Host ""
}

function Run-DockerfileOptimization {
    Write-Host "Optimisation du Dockerfile frontend..." -ForegroundColor Cyan

    # VÃ©rification de l'emplacement du Dockerfile
    $dockerfilePath = "sadie/web/static/Dockerfile"
    if (Test-Path $dockerfilePath) {
        # Sauvegarde du Dockerfile original
        Copy-Item $dockerfilePath "$dockerfilePath.bak"
        Write-Host "Dockerfile original sauvegardÃ© dans $dockerfilePath.bak" -ForegroundColor Green
    } else {
        Write-Host "Aucun Dockerfile existant trouvÃ©. CrÃ©ation d'un nouveau..." -ForegroundColor Yellow
    }

    # CrÃ©ation du nouveau Dockerfile optimisÃ©
    $newDockerfileContent = @"
FROM node:16-alpine

WORKDIR /app/sadie/web/static

# Installation de cross-env pour les variables d'environnement
RUN npm install -g cross-env

# Copie des fichiers de configuration
COPY package*.json ./

# Installation des dÃ©pendances
RUN npm install

# Copie du code source
COPY . .

# Configuration pour Ã©viter les problÃ¨mes de mÃ©moire
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV GENERATE_SOURCEMAP=false

# Configuration du port
EXPOSE 3000

# Commande de dÃ©marrage optimisÃ©e
CMD ["npm", "run", "start:safe"]
"@

    # Ã‰criture du nouveau Dockerfile
    Set-Content $dockerfilePath $newDockerfileContent
    Write-Host "Nouveau Dockerfile optimisÃ© crÃ©Ã© avec succÃ¨s!" -ForegroundColor Green
    
    Read-Host "Appuyez sur EntrÃ©e pour continuer"
}

function Restart-SadieContainers {
    Write-Host "RedÃ©marrage des conteneurs Docker SADIE..." -ForegroundColor Cyan
    
    $sadieContainers = docker ps -a --filter "name=sadie" --format "{{.Names}}"
    
    if ($sadieContainers) {
        foreach ($container in $sadieContainers) {
            Write-Host "RedÃ©marrage du conteneur $container..." -ForegroundColor Yellow
            docker restart $container
        }
        
        Write-Host "RedÃ©marrage terminÃ©." -ForegroundColor Green
    } else {
        Write-Host "Aucun conteneur SADIE trouvÃ©." -ForegroundColor Red
    }
    
    Read-Host "Appuyez sur EntrÃ©e pour continuer"
}

function Clean-DockerResources {
    Write-Host "Nettoyage des ressources Docker inutilisÃ©es..." -ForegroundColor Cyan
    
    Write-Host "Suppression des conteneurs arrÃªtÃ©s..." -ForegroundColor Yellow
    docker container prune -f
    
    Write-Host "Suppression des images non utilisÃ©es..." -ForegroundColor Yellow
    docker image prune -f
    
    Write-Host "Nettoyage terminÃ©." -ForegroundColor Green
    Read-Host "Appuyez sur EntrÃ©e pour continuer"
}

# Boucle principale
$continue = $true

while ($continue) {
    Show-Banner
    Show-MainMenu
    
    $choice = Read-Host "Choisissez une option (1-4)"
    
    switch ($choice) {
        "1" {
            # Optimiser le Dockerfile
            Run-DockerfileOptimization
        }
        "2" {
            # RedÃ©marrer les conteneurs
            Restart-SadieContainers
        }
        "3" {
            # Nettoyer Docker
            Clean-DockerResources
        }
        "4" {
            # Quitter
            $continue = $false
            Write-Host "Au revoir!" -ForegroundColor Cyan
        }
        default {
            Write-Host "Option invalide. Veuillez choisir une option valide." -ForegroundColor Red
            Read-Host "Appuyez sur EntrÃ©e pour continuer"
        }
    }
} 