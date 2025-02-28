!/usr/bin/env pwsh

# Script de diagnostic complet pour SADIE
# ----------------------------------------
# Ce script analyse l'infrastructure SADIE, vÃ©rifie les performances
# et gÃ©nÃ¨re un rapport dÃ©taillÃ© sur l'Ã©tat du systÃ¨me.

Write-Host "Diagnostic complet de SADIE" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Fonction pour crÃ©er une ligne de sÃ©paration
function Write-Separator {
    Write-Host "---------------------------------------------------" -ForegroundColor DarkGray
}

# Fonction pour formater un en-tÃªte de section
function Write-SectionHeader {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Title,
        
        [Parameter(Mandatory=$false)]
        [int]$Level = 1
    )
    
    Write-Host ""
    if ($Level -eq 1) {
        Write-Host "## $Title ##" -ForegroundColor Yellow
    } else {
        Write-Host "* $Title *" -ForegroundColor Magenta
    }
    Write-Separator
}

# CrÃ©ation du dossier de rapports s'il n'existe pas
$reportDir = "diagnostic-reports"
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

# GÃ©nÃ©rer un nom de fichier de rapport avec la date et l'heure actuelles
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = Join-Path -Path $reportDir -ChildPath "sadie_diagnostic_${timestamp}.txt"

# DÃ©marrer la capture du rapport
Start-Transcript -Path $reportFile | Out-Null
Write-Host "GÃ©nÃ©ration du rapport de diagnostic Ã  $reportFile" -ForegroundColor Green

# VÃ©rification de l'environnement de base
Write-SectionHeader "Informations sur l'environnement"
Write-Host "Date et heure : $(Get-Date)" -ForegroundColor White
Write-Host "OS : $(Get-CimInstance Win32_OperatingSystem | Select-Object Caption)" -ForegroundColor White
Write-Host "PowerShell version : $($PSVersionTable.PSVersion)" -ForegroundColor White
Write-Host "Utilisateur : $env:USERNAME" -ForegroundColor White
Write-Host "RÃ©pertoire de travail : $(Get-Location)" -ForegroundColor White

# VÃ©rification de Docker
Write-SectionHeader "VÃ©rification de Docker"
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker n'est pas en cours d'exÃ©cution ou n'est pas installÃ©." -ForegroundColor Red
    } else {
        Write-Host "Docker installÃ©: $dockerVersion" -ForegroundColor Green
        
        Write-SectionHeader "Ã‰tat de Docker" 2
        docker info | Select-String "Containers:|Running:|Paused:|Stopped:|Images:|Server Version:|Kernel Version:"
        
        Write-SectionHeader "Utilisation des ressources Docker" 2
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    }
} catch {
    Write-Host "Erreur lors de la vÃ©rification de Docker: $_" -ForegroundColor Red
}

# VÃ©rification des conteneurs SADIE
Write-SectionHeader "Conteneurs SADIE"
try {
    $sadieContainers = docker ps -a --filter "name=sadie" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}"
    if ($sadieContainers) {
        Write-Host $sadieContainers -ForegroundColor White
        
        Write-SectionHeader "Logs des conteneurs (30 derniÃ¨res lignes)" 2
        $containerNames = docker ps -a --filter "name=sadie" --format "{{.Names}}"
        foreach ($container in $containerNames) {
            Write-Host "Logs pour $container :" -ForegroundColor Cyan
            docker logs --tail 30 $container
            Write-Separator
        }
    } else {
        Write-Host "Aucun conteneur SADIE trouvÃ©." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Erreur lors de la vÃ©rification des conteneurs SADIE: $_" -ForegroundColor Red
}

# VÃ©rification des images Docker
Write-SectionHeader "Images Docker"
try {
    docker images --filter "reference=*sadie*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
} catch {
    Write-Host "Erreur lors de la rÃ©cupÃ©ration des images: $_" -ForegroundColor Red
}

# VÃ©rification des volumes Docker
Write-SectionHeader "Volumes Docker"
try {
    docker volume ls --filter "name=sadie" --format "table {{.Name}}\t{{.Driver}}\t{{.Mountpoint}}"
} catch {
    Write-Host "Erreur lors de la rÃ©cupÃ©ration des volumes: $_" -ForegroundColor Red
}

# VÃ©rification des rÃ©seaux Docker
Write-SectionHeader "RÃ©seaux Docker"
try {
    docker network ls --filter "name=sadie" --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"
} catch {
    Write-Host "Erreur lors de la rÃ©cupÃ©ration des rÃ©seaux: $_" -ForegroundColor Red
}

# VÃ©rification de l'espace disque
Write-SectionHeader "Espace disque"
try {
    Get-PSDrive C | Format-Table -Property Name, Used, Free, @{
        Name = "UsedGB"
        Expression = {[math]::Round($_.Used / 1GB, 2)}
    }, @{
        Name = "FreeGB"
        Expression = {[math]::Round($_.Free / 1GB, 2)}
    }, @{
        Name = "FreePercent"
        Expression = {[math]::Round(($_.Free / ($_.Used + $_.Free)) * 100, 2)}
    } -AutoSize
} catch {
    Write-Host "Erreur lors de la vÃ©rification de l'espace disque: $_" -ForegroundColor Red
}

# VÃ©rification des fichiers de configuration
Write-SectionHeader "Fichiers de configuration"
$configFiles = @(
    "sadie/web/static/.env",
    "frontend/package.json",
    "docker-compose.yml"
)

foreach ($file in $configFiles) {
    if (Test-Path $file) {
        Write-Host "Fichier trouvÃ©: $file" -ForegroundColor Green
        try {
            $fileContent = Get-Content $file -ErrorAction Stop
            if ($file -like "*.json") {
                # Pour les fichiers JSON, on peut vÃ©rifier s'ils sont valides
                try {
                    $null = $fileContent | ConvertFrom-Json
                    Write-Host "  - JSON valide" -ForegroundColor Green
                } catch {
                    Write-Host "  - JSON invalide: $_" -ForegroundColor Red
                }
            }
            
            # VÃ©rifier la taille du fichier
            $fileSize = (Get-Item $file).Length / 1KB
            Write-Host "  - Taille: $([math]::Round($fileSize, 2)) KB" -ForegroundColor White
            
            # VÃ©rifier la date de derniÃ¨re modification
            $lastModified = (Get-Item $file).LastWriteTime
            Write-Host "  - DerniÃ¨re modification: $lastModified" -ForegroundColor White
        } catch {
            Write-Host "Erreur lors de la lecture de $file : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Fichier non trouvÃ©: $file" -ForegroundColor Yellow
    }
}

# VÃ©rification des connexions rÃ©seau
Write-SectionHeader "Connexions rÃ©seau"
try {
    # VÃ©rifier si le port 3000 (frontend) est ouvert
    $frontendPort = (Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0
    if ($frontendPort) {
        Write-Host "Port 3000 (Frontend) est ouvert et en Ã©coute" -ForegroundColor Green
    } else {
        Write-Host "Port 3000 (Frontend) n'est pas en Ã©coute" -ForegroundColor Yellow
    }
    
    # VÃ©rifier si le port 8000 (API) est ouvert
    $apiPort = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0
    if ($apiPort) {
        Write-Host "Port 8000 (API) est ouvert et en Ã©coute" -ForegroundColor Green
    } else {
        Write-Host "Port 8000 (API) n'est pas en Ã©coute" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Erreur lors de la vÃ©rification des connexions rÃ©seau: $_" -ForegroundColor Red
}

# VÃ©rification des performances de la machine
Write-SectionHeader "Performances de la machine"
try {
    # CPU usage
    $cpu = Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average
    Write-Host "Utilisation CPU: $($cpu.Average)%" -ForegroundColor White
    
    # MÃ©moire
    $memory = Get-CimInstance Win32_OperatingSystem
    $memoryUsed = $memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory
    $memoryUsedGB = [math]::Round($memoryUsed / 1MB, 2)
    $memoryTotalGB = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
    $memoryPercent = [math]::Round(($memoryUsed / $memory.TotalVisibleMemorySize) * 100, 2)
    
    Write-Host "Utilisation MÃ©moire: $memoryUsedGB GB / $memoryTotalGB GB ($memoryPercent%)" -ForegroundColor White
} catch {
    Write-Host "Erreur lors de la rÃ©cupÃ©ration des performances: $_" -ForegroundColor Red
}

# VÃ©rification de la configuration des collecteurs
Write-SectionHeader "Configuration des collecteurs"
$collectorsPaths = @(
    "sadie/core/collectors/__init__.py",
    "sadie/data/collectors/__init__.py"
)

foreach ($path in $collectorsPaths) {
    if (Test-Path $path) {
        Write-Host "Fichier collecteur trouvÃ©: $path" -ForegroundColor Green
        try {
            $content = Get-Content $path -Raw
            Write-Host "Contenu de $path:" -ForegroundColor White
            Write-Host $content -ForegroundColor Gray
        } catch {
            Write-Host "Erreur lors de la lecture de $path : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Fichier collecteur non trouvÃ©: $path" -ForegroundColor Yellow
    }
}

# GÃ©nÃ©ration de recommandations
Write-SectionHeader "Recommandations"

# VÃ©rification des conteneurs arrÃªtÃ©s
$stoppedContainers = docker ps -a --filter "status=exited" --filter "name=sadie" --format "{{.Names}}"
if ($stoppedContainers) {
    Write-Host "Conteneurs arrÃªtÃ©s dÃ©tectÃ©s:" -ForegroundColor Yellow
    foreach ($container in $stoppedContainers) {
        Write-Host "  - $container" -ForegroundColor Yellow
        Write-Host "    Recommandation: RedÃ©marrez ce conteneur avec 'docker start $container'" -ForegroundColor Cyan
    }
}

# VÃ©rification de l'espace disque faible
if ((Get-PSDrive C).Free / 1GB -lt 10) {
    Write-Host "Espace disque faible (moins de 10 GB disponible)" -ForegroundColor Red
    Write-Host "  Recommandation: LibÃ©rez de l'espace disque ou nettoyez Docker avec 'docker system prune'" -ForegroundColor Cyan
}

# Optimisations suggÃ©rÃ©es
Write-Host "Optimisations suggÃ©rÃ©es:" -ForegroundColor Green
Write-Host "  - ExÃ©cutez './optimize-package-json.ps1' pour optimiser le fichier package.json" -ForegroundColor Cyan
Write-Host "  - ExÃ©cutez './optimize-dockerfile.ps1' pour optimiser le Dockerfile" -ForegroundColor Cyan
Write-Host "  - ExÃ©cutez './restart-containers.ps1' pour redÃ©marrer les conteneurs avec les configurations optimisÃ©es" -ForegroundColor Cyan

# Terminer la capture du rapport
Stop-Transcript | Out-Null

Write-Host ""
Write-Host "Diagnostic terminÃ©! Rapport enregistrÃ© dans: $reportFile" -ForegroundColor Green
Write-Host "Vous pouvez consulter le rapport avec la commande: notepad $reportFile" -ForegroundColor Cyan 