!/usr/bin/env pwsh

# Script d'optimisation de la configuration rÃ©seau pour SADIE
# ---------------------------------------------------------
# Ce script optimise les paramÃ¨tres rÃ©seau des conteneurs Docker
# de SADIE pour amÃ©liorer les performances et la stabilitÃ©.

Write-Host "Optimisation de la configuration rÃ©seau de SADIE" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

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

# VÃ©rifier si docker-compose.yml existe
$dockerComposePath = "docker-compose.yml"
if (-not (Test-Path $dockerComposePath)) {
    $dockerComposePath = "frontend/docker-compose.yml"
    if (-not (Test-Path $dockerComposePath)) {
        Write-Host "Erreur: Aucun fichier docker-compose.yml trouvÃ©." -ForegroundColor Red
        
        # Si docker-compose.yml n'existe pas, crÃ©er un fichier de base
        $createNewFile = Read-Host "Voulez-vous crÃ©er un nouveau fichier docker-compose.yml? (o/n)"
        if ($createNewFile -eq "o") {
            $dockerComposePath = "docker-compose.yml"
            $dockerComposeContent = @"
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
    container_name: sadie-frontend
    ports:
      - 3000:3000
    environment:
      - NODE_OPTIONS=--max-old-space-size=4096
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_WS_URL=ws://localhost:8000/ws
    restart: unless-stopped
    networks:
      - sadie-network
    dns:
      - 8.8.8.8
      - 1.1.1.1

networks:
  sadie-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
    driver_opts:
      com.docker.network.driver.mtu: 1500
"@
            Set-Content -Path $dockerComposePath -Value $dockerComposeContent
            Write-Host "Nouveau fichier docker-compose.yml crÃ©Ã©." -ForegroundColor Green
        } else {
            Write-Host "OpÃ©ration annulÃ©e. Aucun fichier docker-compose.yml trouvÃ©." -ForegroundColor Yellow
            exit 1
        }
    }
}

Write-Host "Fichier docker-compose.yml trouvÃ© Ã  $dockerComposePath" -ForegroundColor Green

# Sauvegarder le fichier original
$backupPath = "$dockerComposePath.bak"
Copy-Item -Path $dockerComposePath -Destination $backupPath -Force
Write-Host "Sauvegarde crÃ©Ã©e Ã  $backupPath" -ForegroundColor Yellow

# Lire le contenu actuel
$composeContent = Get-Content -Path $dockerComposePath -Raw

# VÃ©rifier si le fichier est en format YAML
try {
    $yaml = ConvertFrom-Yaml -Yaml $composeContent
} catch {
    # Si la commande ConvertFrom-Yaml Ã©choue, vÃ©rifier si le module est installÃ©
    try {
        Import-Module powershell-yaml -ErrorAction Stop
    } catch {
        Write-Host "Le module 'powershell-yaml' n'est pas installÃ©. Installation en cours..." -ForegroundColor Yellow
        try {
            Install-Module -Name powershell-yaml -Scope CurrentUser -Force
            Import-Module powershell-yaml
            Write-Host "Module powershell-yaml installÃ© avec succÃ¨s." -ForegroundColor Green
        } catch {
            Write-Host "Erreur lors de l'installation du module powershell-yaml. Traitement du fichier en tant que texte brut." -ForegroundColor Red
            $useYaml = $false
        }
    }
    
    # Essayer Ã  nouveau de convertir le YAML
    try {
        $yaml = ConvertFrom-Yaml -Yaml $composeContent
        $useYaml = $true
    } catch {
        Write-Host "Erreur lors de l'analyse du fichier YAML. Traitement du fichier en tant que texte brut." -ForegroundColor Red
        $useYaml = $false
    }
}

# Optimiser la configuration rÃ©seau
if ($useYaml) {
    # MÃ©thode avec module YAML - modification plus propre
    Write-Host "Optimisation du fichier YAML..." -ForegroundColor Yellow
    
    # VÃ©rifier que les services existent
    if (-not $yaml.services) {
        $yaml.services = @{}
    }
    
    # Optimiser chaque service
    foreach ($serviceName in $yaml.services.Keys) {
        $service = $yaml.services[$serviceName]
        
        # Ajouter une configuration DNS pour une rÃ©solution de noms plus rapide
        if (-not $service.dns) {
            $service.dns = @("8.8.8.8", "1.1.1.1")
            Write-Host "Configuration DNS ajoutÃ©e pour le service $serviceName." -ForegroundColor Green
        }
        
        # Ajouter la configuration de restart pour amÃ©liorer la rÃ©silience
        if (-not $service.restart) {
            $service.restart = "unless-stopped"
            Write-Host "Configuration de redÃ©marrage ajoutÃ©e pour le service $serviceName." -ForegroundColor Green
        }
        
        # VÃ©rifier si le service a une configuration rÃ©seau
        if (-not $service.networks) {
            # Ajouter le service au rÃ©seau SADIE s'il n'est pas dÃ©jÃ  configurÃ©
            $service.networks = @("sadie-network")
            Write-Host "Service $serviceName ajoutÃ© au rÃ©seau sadie-network." -ForegroundColor Green
        }
    }
    
    # VÃ©rifier que la section networks existe
    if (-not $yaml.networks) {
        $yaml.networks = @{}
    }
    
    # Optimiser ou crÃ©er le rÃ©seau sadie-network
    if (-not $yaml.networks["sadie-network"]) {
        $yaml.networks["sadie-network"] = @{
            driver = "bridge"
            ipam = @{
                config = @(
                    @{
                        subnet = "172.28.0.0/16"
                    }
                )
            }
            driver_opts = @{
                "com.docker.network.driver.mtu" = 1500
            }
        }
        Write-Host "RÃ©seau sadie-network crÃ©Ã© avec des paramÃ¨tres optimisÃ©s." -ForegroundColor Green
    } else {
        # Optimiser le rÃ©seau existant
        $network = $yaml.networks["sadie-network"]
        
        if (-not $network.driver_opts) {
            $network.driver_opts = @{}
        }
        
        $network.driver_opts["com.docker.network.driver.mtu"] = 1500
        Write-Host "MTU du rÃ©seau optimisÃ© Ã  1500." -ForegroundColor Green
    }
    
    # Convertir le YAML modifiÃ© en chaÃ®ne
    $newComposeContent = ConvertTo-Yaml -Data $yaml
    
    # Sauvegarder le nouveau contenu
    Set-Content -Path $dockerComposePath -Value $newComposeContent
} else {
    # MÃ©thode de modification de texte brut
    Write-Host "Optimisation du fichier en tant que texte brut..." -ForegroundColor Yellow
    
    # VÃ©rifier si le rÃ©seau sadie-network existe dÃ©jÃ 
    $networkExists = $composeContent -match "networks:\s*sadie-network"
    
    if (-not $networkExists) {
        # Ajouter la section rÃ©seaux si elle n'existe pas
        $networkConfig = @"

networks:
  sadie-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
    driver_opts:
      com.docker.network.driver.mtu: 1500
"@
        $composeContent += $networkConfig
        Write-Host "Configuration rÃ©seau ajoutÃ©e." -ForegroundColor Green
    } else {
        # Modifier la configuration rÃ©seau existante
        $composeContent = $composeContent -replace "(networks:\s*sadie-network:[\s\S]*?(?=\n\w|\Z))", @"
networks:
  sadie-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
    driver_opts:
      com.docker.network.driver.mtu: 1500
"@
        Write-Host "Configuration rÃ©seau mise Ã  jour." -ForegroundColor Green
    }
    
    # Ajouter la configuration DNS et le redÃ©marrage automatique pour chaque service
    $serviceMatches = [regex]::Matches($composeContent, "^\s*\w+:\s*$", [System.Text.RegularExpressions.RegexOptions]::Multiline)
    
    foreach ($match in $serviceMatches) {
        $serviceName = $match.Value.Trim().TrimEnd(":")
        
        # VÃ©rifier si le service a dÃ©jÃ  une configuration DNS
        $dnsExists = $composeContent -match "$serviceName:[\s\S]*?dns:"
        
        if (-not $dnsExists) {
            # Trouver la fin du bloc de service
            $serviceEndMatch = [regex]::Match($composeContent.Substring($match.Index), "^\s*\w+:\s*$", [System.Text.RegularExpressions.RegexOptions]::Multiline)
            
            if ($serviceEndMatch.Success) {
                $serviceEndIndex = $match.Index + $serviceEndMatch.Index
                
                $dnsConfig = @"
    dns:
      - 8.8.8.8
      - 1.1.1.1
    restart: unless-stopped
    networks:
      - sadie-network
"@
                $composeContent = $composeContent.Insert($serviceEndIndex, "$dnsConfig`n")
                Write-Host "Configuration DNS, redÃ©marrage et rÃ©seau ajoutÃ©es pour le service $serviceName." -ForegroundColor Green
            }
        }
    }
    
    # Sauvegarder le nouveau contenu
    Set-Content -Path $dockerComposePath -Value $composeContent
}

Write-Host "Optimisation de la configuration rÃ©seau terminÃ©e." -ForegroundColor Green

# VÃ©rification de la configuration rÃ©seau actuelle de Docker
Write-Host "`nVÃ©rification des rÃ©seaux Docker actuels:" -ForegroundColor Yellow
docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"

# Recreer le rÃ©seau sadie-network s'il existe dÃ©jÃ  pour appliquer les nouveaux paramÃ¨tres
$sadieNetworkExists = docker network ls --filter "name=sadie-network" --format "{{.Name}}" | Select-String "sadie-network"

if ($sadieNetworkExists) {
    Write-Host "`nRecrÃ©ation du rÃ©seau sadie-network pour appliquer les nouveaux paramÃ¨tres..." -ForegroundColor Yellow
    
    # VÃ©rifier si des conteneurs utilisent ce rÃ©seau
    $containersUsingNetwork = docker network inspect sadie-network --format "{{range .Containers}}{{.Name}} {{end}}" 2>$null
    
    if ($containersUsingNetwork) {
        Write-Host "Les conteneurs suivants utilisent le rÃ©seau sadie-network: $containersUsingNetwork" -ForegroundColor Yellow
        Write-Host "DÃ©connexion des conteneurs du rÃ©seau..." -ForegroundColor Yellow
        
        $containers = $containersUsingNetwork -split " "
        foreach ($container in $containers) {
            if ($container) {
                docker network disconnect -f sadie-network $container 2>$null
                Write-Host "Conteneur $container dÃ©connectÃ© du rÃ©seau sadie-network." -ForegroundColor Green
            }
        }
    }
    
    # Supprimer le rÃ©seau
    docker network rm sadie-network 2>$null
    Write-Host "RÃ©seau sadie-network supprimÃ©." -ForegroundColor Green
    
    # RecrÃ©er le rÃ©seau avec les paramÃ¨tres optimisÃ©s
    docker network create --driver bridge --subnet 172.28.0.0/16 --opt "com.docker.network.driver.mtu=1500" sadie-network
    Write-Host "RÃ©seau sadie-network recrÃ©Ã© avec des paramÃ¨tres optimisÃ©s." -ForegroundColor Green
    
    # Reconnecter les conteneurs au rÃ©seau
    if ($containersUsingNetwork) {
        Write-Host "Reconnexion des conteneurs au rÃ©seau..." -ForegroundColor Yellow
        
        foreach ($container in $containers) {
            if ($container) {
                docker network connect sadie-network $container 2>$null
                Write-Host "Conteneur $container reconnectÃ© au rÃ©seau sadie-network." -ForegroundColor Green
            }
        }
    }
} else {
    # CrÃ©er le rÃ©seau s'il n'existe pas encore
    docker network create --driver bridge --subnet 172.28.0.0/16 --opt "com.docker.network.driver.mtu=1500" sadie-network
    Write-Host "RÃ©seau sadie-network crÃ©Ã© avec des paramÃ¨tres optimisÃ©s." -ForegroundColor Green
}

# Instructions pour appliquer les changements
Write-Host "`nPour appliquer complÃ¨tement les changements, exÃ©cutez les commandes suivantes:" -ForegroundColor Cyan
Write-Host "1. RecrÃ©ez et redÃ©marrez vos conteneurs avec:" -ForegroundColor White
Write-Host "   docker-compose up -d --force-recreate" -ForegroundColor White
Write-Host "2. Ou utilisez le script de redÃ©marrage des conteneurs:" -ForegroundColor White
Write-Host "   ./restart-containers.ps1" -ForegroundColor White

Write-Host "`nL'optimisation de la configuration rÃ©seau est terminÃ©e!" -ForegroundColor Green 