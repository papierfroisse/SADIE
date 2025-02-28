!/usr/bin/env pwsh

Write-Host "=== NETTOYAGE DES RESSOURCES DOCKER INUTILISÃ‰ES ===" -ForegroundColor Cyan

# VÃ©rifier si Docker est installÃ© et en cours d'exÃ©cution
try {
    $dockerStatus = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "âŒ Docker n'est pas en cours d'exÃ©cution ou n'est pas installÃ©." -ForegroundColor Red
        exit 1
    } else {
        Write-Host "âœ… Docker est en cours d'exÃ©cution." -ForegroundColor Green
    }
} catch {
    Write-Host "âŒ Une erreur s'est produite lors de la vÃ©rification de Docker: $_" -ForegroundColor Red
    exit 1
}

# Fonction pour afficher les statistiques Docker avant et aprÃ¨s le nettoyage
function Show-DockerStats {
    param (
        [string]$phase = "AVANT"
    )
    
    Write-Host "`n=== STATISTIQUES DOCKER ($phase NETTOYAGE) ===" -ForegroundColor Yellow
    
    # Compter les conteneurs
    $containers = docker ps -a --format "{{.ID}}" | Measure-Object | Select-Object -ExpandProperty Count
    Write-Host "Conteneurs: $containers" -ForegroundColor White
    
    # Compter les images
    $images = docker images --format "{{.ID}}" | Measure-Object | Select-Object -ExpandProperty Count
    Write-Host "Images: $images" -ForegroundColor White
    
    # Compter les volumes
    $volumes = docker volume ls --format "{{.Name}}" | Measure-Object | Select-Object -ExpandProperty Count
    Write-Host "Volumes: $volumes" -ForegroundColor White
    
    # Compter les rÃ©seaux (soustrayant les 3 rÃ©seaux par dÃ©faut)
    $networks = (docker network ls --format "{{.ID}}" | Measure-Object | Select-Object -ExpandProperty Count) - 3
    if ($networks -lt 0) { $networks = 0 }
    Write-Host "RÃ©seaux (non-default): $networks" -ForegroundColor White
    
    # Taille du cache de build
    try {
        $buildCache = docker system df --format "{{.BuildCache}}" | Select-String -Pattern "\d+(\.\d+)?[KMGTP]iB" | ForEach-Object { $_.Matches.Value }
        if ($buildCache) {
            Write-Host "Cache de build: $buildCache" -ForegroundColor White
        }
    } catch {
        Write-Host "Impossible de rÃ©cupÃ©rer la taille du cache de build" -ForegroundColor Yellow
    }
    
    Write-Host "===============================================" -ForegroundColor Yellow
}

# Afficher les stats avant nettoyage
Show-DockerStats -phase "AVANT"

# Demander confirmation Ã  l'utilisateur
Write-Host "`nATTENTION: Cette opÃ©ration va supprimer les conteneurs arrÃªtÃ©s, les images non utilisÃ©es, les rÃ©seaux inutilisÃ©s et les volumes orphelins." -ForegroundColor Yellow
$confirmation = Read-Host "Souhaitez-vous continuer? (O/N)"

if ($confirmation -ne "O" -and $confirmation -ne "o") {
    Write-Host "OpÃ©ration annulÃ©e par l'utilisateur." -ForegroundColor Yellow
    exit 0
}

# ArrÃªter les conteneurs non essentiels (exclure les conteneurs SADIE en cours d'exÃ©cution)
Write-Host "`n1. ArrÃªt des conteneurs non essentiels..." -ForegroundColor Cyan
$runningSadieContainers = docker ps --format "{{.ID}} {{.Names}}" | Select-String -Pattern "sadie"

if ($runningSadieContainers) {
    Write-Host "Conteneurs SADIE en cours d'exÃ©cution dÃ©tectÃ©s. Ils ne seront pas arrÃªtÃ©s." -ForegroundColor Yellow
    # ArrÃªter tous les conteneurs sauf ceux contenant "sadie" dans leur nom
    $nonSadieContainers = docker ps --format "{{.ID}} {{.Names}}" | Where-Object { $_ -notmatch "sadie" }
    if ($nonSadieContainers) {
        $nonSadieContainers | ForEach-Object {
            $containerId = ($_ -split " ")[0]
            docker stop $containerId | Out-Null
            Write-Host "Conteneur $containerId arrÃªtÃ©." -ForegroundColor Green
        }
    } else {
        Write-Host "Aucun conteneur non-SADIE en cours d'exÃ©cution." -ForegroundColor Green
    }
} else {
    Write-Host "Aucun conteneur SADIE en cours d'exÃ©cution. ArrÃªt de tous les conteneurs..." -ForegroundColor Yellow
    docker stop $(docker ps -q) 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Tous les conteneurs ont Ã©tÃ© arrÃªtÃ©s." -ForegroundColor Green
    } else {
        Write-Host "Aucun conteneur en cours d'exÃ©cution Ã  arrÃªter." -ForegroundColor Green
    }
}

# Supprimer les conteneurs arrÃªtÃ©s
Write-Host "`n2. Suppression des conteneurs arrÃªtÃ©s..." -ForegroundColor Cyan
docker container prune -f
Write-Host "âœ… Conteneurs arrÃªtÃ©s supprimÃ©s." -ForegroundColor Green

# Supprimer les images non utilisÃ©es
Write-Host "`n3. Suppression des images non utilisÃ©es..." -ForegroundColor Cyan
docker image prune -a --filter "until=24h" -f
Write-Host "âœ… Images non utilisÃ©es (>24h) supprimÃ©es." -ForegroundColor Green

# Supprimer les volumes non utilisÃ©s
Write-Host "`n4. Suppression des volumes non utilisÃ©s..." -ForegroundColor Cyan
docker volume prune -f
Write-Host "âœ… Volumes non utilisÃ©s supprimÃ©s." -ForegroundColor Green

# Supprimer les rÃ©seaux non utilisÃ©s
Write-Host "`n5. Suppression des rÃ©seaux non utilisÃ©s..." -ForegroundColor Cyan
docker network prune -f
Write-Host "âœ… RÃ©seaux non utilisÃ©s supprimÃ©s." -ForegroundColor Green

# Nettoyer le cache de build
Write-Host "`n6. Nettoyage du cache de build..." -ForegroundColor Cyan
docker builder prune -f --keep-storage 1GB
Write-Host "âœ… Cache de build nettoyÃ© (conservant 1GB pour les builds futurs)." -ForegroundColor Green

# Afficher les stats aprÃ¨s nettoyage
Show-DockerStats -phase "APRÃˆS"

# Afficher l'espace disque rÃ©cupÃ©rÃ©
Write-Host "`n=== RÃ‰SUMÃ‰ DU NETTOYAGE ===" -ForegroundColor Cyan
Write-Host "Le nettoyage des ressources Docker est terminÃ©!" -ForegroundColor Green

# Afficher les conseils d'optimisation
Write-Host "`nConseils d'optimisation supplÃ©mentaires:" -ForegroundColor Yellow
Write-Host "1. RÃ©duisez la taille des images Docker en utilisant des images de base plus lÃ©gÃ¨res (alpine)" -ForegroundColor White
Write-Host "2. Utilisez des builds multi-Ã©tapes pour rÃ©duire la taille finale des images" -ForegroundColor White
Write-Host "3. Pour nettoyer complÃ¨tement Docker (DANGER - supprime TOUT): docker system prune -a --volumes" -ForegroundColor White
Write-Host "4. ExÃ©cutez ce script pÃ©riodiquement pour maintenir votre systÃ¨me propre" -ForegroundColor White 