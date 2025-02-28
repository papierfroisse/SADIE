!/usr/bin/env pwsh

Write-Host "=== VÃ‰RIFICATION DES PERFORMANCES DU RÃ‰SEAU DOCKER ===" -ForegroundColor Cyan

# ParamÃ¨tres et constantes
$MIN_BANDWIDTH = 500  # Bande passante minimale attendue (MB/s)
$TARGET_LATENCY = 5   # Latence cible (ms)
$TIMEOUT_SECONDS = 5  # Timeout pour les tests (s)

# VÃ©rifier si Docker est installÃ© et en cours d'exÃ©cution
try {
    $dockerInfo = docker info 2>&1
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

# VÃ©rifier si l'image nicolaka/netshoot est disponible ou la tÃ©lÃ©charger
Write-Host "`nVÃ©rification de l'image de test rÃ©seau..." -ForegroundColor Yellow
$netshootImage = docker images nicolaka/netshoot --format "{{.Repository}}"
if (-not $netshootImage) {
    Write-Host "TÃ©lÃ©chargement de l'image nicolaka/netshoot pour les tests rÃ©seau..." -ForegroundColor Yellow
    docker pull nicolaka/netshoot
    if ($LASTEXITCODE -ne 0) {
        Write-Host "âŒ Impossible de tÃ©lÃ©charger l'image de test rÃ©seau." -ForegroundColor Red
        exit 1
    }
}

# CrÃ©er un rÃ©seau de test temporaire
Write-Host "`nCrÃ©ation d'un rÃ©seau de test temporaire..." -ForegroundColor Yellow
$testNetworkName = "sadie-network-test"
docker network create --driver bridge $testNetworkName
if ($LASTEXITCODE -ne 0) {
    Write-Host "âŒ Impossible de crÃ©er le rÃ©seau de test." -ForegroundColor Red
    exit 1
}
Write-Host "âœ… RÃ©seau de test '$testNetworkName' crÃ©Ã©." -ForegroundColor Green

# Fonction pour lancer une commande dans un conteneur
function Invoke-DockerCommand {
    param (
        [string]$containerName,
        [string]$command
    )
    
    $result = docker exec $containerName sh -c $command 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "âŒ Erreur lors de l'exÃ©cution de la commande: $command" -ForegroundColor Red
        return $null
    }
    return $result
}

# CrÃ©er les conteneurs de test
Write-Host "`nCrÃ©ation des conteneurs de test..." -ForegroundColor Yellow
docker run -d --name sadie-network-test1 --network $testNetworkName nicolaka/netshoot sleep 3600
docker run -d --name sadie-network-test2 --network $testNetworkName nicolaka/netshoot sleep 3600

if ($LASTEXITCODE -ne 0) {
    Write-Host "âŒ Impossible de crÃ©er les conteneurs de test." -ForegroundColor Red
    # Nettoyage
    docker network rm $testNetworkName 2>&1 | Out-Null
    exit 1
}
Write-Host "âœ… Conteneurs de test crÃ©Ã©s." -ForegroundColor Green

# RÃ©cupÃ©rer les adresses IP des conteneurs
$container1IP = Invoke-DockerCommand -containerName "sadie-network-test1" -command "hostname -i"
$container2IP = Invoke-DockerCommand -containerName "sadie-network-test2" -command "hostname -i"

Write-Host "`nTest conteneur 1 IP: $container1IP" -ForegroundColor White
Write-Host "Test conteneur 2 IP: $container2IP" -ForegroundColor White

# Fonction pour faire le rapport des rÃ©sultats de test avec code couleur
function Report-TestResult {
    param (
        [string]$testName,
        [string]$result,
        [bool]$passed,
        [string]$details = ""
    )
    
    $statusColor = if ($passed) { "Green" } else { "Red" }
    $statusSymbol = if ($passed) { "âœ…" } else { "âŒ" }
    
    Write-Host "$statusSymbol $testName : " -NoNewline
    Write-Host $result -ForegroundColor $statusColor
    
    if ($details) {
        Write-Host "   $details" -ForegroundColor Gray
    }
}

# Test de latence rÃ©seau (ping)
Write-Host "`n=== TEST DE LATENCE RÃ‰SEAU ===" -ForegroundColor Yellow
$pingCommand = "ping -c 10 $container2IP | grep -oP 'time=\K[0-9\.]+' | awk '{ sum += \$1; n++ } END { if (n > 0) print sum / n; }'"
$pingResult = Invoke-DockerCommand -containerName "sadie-network-test1" -command $pingCommand

if ($pingResult) {
    $averageLatency = [double]$pingResult
    $passedLatency = $averageLatency -lt $TARGET_LATENCY
    Report-TestResult -testName "Temps de rÃ©ponse moyen (10 pings)" -result "$averageLatency ms" -passed $passedLatency -details "Cible: < $TARGET_LATENCY ms"
} else {
    Report-TestResult -testName "Test de latence rÃ©seau" -result "Ã‰CHEC" -passed $false -details "Le test de ping a Ã©chouÃ©."
}

# Test de bande passante (iperf) - on installera iperf au besoin
Write-Host "`n=== TEST DE BANDE PASSANTE ===" -ForegroundColor Yellow

# Installer iperf si nÃ©cessaire 
Invoke-DockerCommand -containerName "sadie-network-test1" -command "which iperf || apk add --no-cache iperf" | Out-Null
Invoke-DockerCommand -containerName "sadie-network-test2" -command "which iperf || apk add --no-cache iperf" | Out-Null

# DÃ©marrer le serveur iperf sur le conteneur 2
Invoke-DockerCommand -containerName "sadie-network-test2" -command "iperf -s -D" | Out-Null
Start-Sleep -Seconds 1

# ExÃ©cuter le test iperf depuis le conteneur 1
$iperfCommand = "iperf -c $container2IP -t 5 | grep -oP '\s\K[0-9\.]+(?= Mbits/sec)'"
$iperfResult = Invoke-DockerCommand -containerName "sadie-network-test1" -command $iperfCommand

if ($iperfResult) {
    $bandwidth = [double]$iperfResult
    $passedBandwidth = $bandwidth -gt $MIN_BANDWIDTH
    Report-TestResult -testName "Bande passante du rÃ©seau" -result "$bandwidth Mbits/sec" -passed $passedBandwidth -details "Cible: > $MIN_BANDWIDTH Mbits/sec"
} else {
    Report-TestResult -testName "Test de bande passante" -result "Ã‰CHEC" -passed $false -details "Le test iperf a Ã©chouÃ©."
}

# Test de perte de paquets
Write-Host "`n=== TEST DE PERTE DE PAQUETS ===" -ForegroundColor Yellow
$packetLossCommand = "ping -c 100 -i 0.01 $container2IP | grep -oP '[0-9]+(?=% packet loss)'"
$packetLossResult = Invoke-DockerCommand -containerName "sadie-network-test1" -command $packetLossCommand

if ($packetLossResult) {
    $packetLoss = [double]$packetLossResult
    $passedPacketLoss = $packetLoss -lt 2  # Moins de 2% de perte est acceptable
    Report-TestResult -testName "Perte de paquets" -result "$packetLoss%" -passed $passedPacketLoss -details "Cible: < 2%"
} else {
    Report-TestResult -testName "Test de perte de paquets" -result "Ã‰CHEC" -passed $false -details "Le test de perte de paquets a Ã©chouÃ©."
}

# Test de DNS
Write-Host "`n=== TEST DE RÃ‰SOLUTION DNS ===" -ForegroundColor Yellow
$dnsCommand = "time dig +short google.com | head -1"
$dnsStartTime = Get-Date
$dnsResult = Invoke-DockerCommand -containerName "sadie-network-test1" -command $dnsCommand
$dnsEndTime = Get-Date
$dnsResolutionTime = ($dnsEndTime - $dnsStartTime).TotalMilliseconds

if ($dnsResult) {
    $passedDNS = $dnsResolutionTime -lt 1000  # Moins de 1 seconde est acceptable
    Report-TestResult -testName "RÃ©solution DNS" -result "$dnsResolutionTime ms" -passed $passedDNS -details "Cible: < 1000 ms"
} else {
    Report-TestResult -testName "Test de rÃ©solution DNS" -result "Ã‰CHEC" -passed $false -details "Le test DNS a Ã©chouÃ©."
}

# Test MTU
Write-Host "`n=== TEST MTU ===" -ForegroundColor Yellow
$mtuCommand = "ip addr show eth0 | grep -oP 'mtu\s\K[0-9]+'"
$mtuResult = Invoke-DockerCommand -containerName "sadie-network-test1" -command $mtuCommand

if ($mtuResult) {
    $mtu = [int]$mtuResult
    $passedMTU = $mtu -ge 1500
    Report-TestResult -testName "MTU du rÃ©seau" -result "$mtu bytes" -passed $passedMTU -details "Cible: >= 1500 bytes"
} else {
    Report-TestResult -testName "Test MTU" -result "Ã‰CHEC" -passed $false -details "Le test MTU a Ã©chouÃ©."
}

# VÃ©rifier la configuration rÃ©seau de SADIE
Write-Host "`n=== CONFIGURATION RÃ‰SEAU SADIE ===" -ForegroundColor Yellow

# VÃ©rifier si le rÃ©seau sadie-network existe
$sadieNetwork = docker network ls --format "{{.Name}}" | Where-Object { $_ -match "sadie" }

if ($sadieNetwork) {
    Write-Host "RÃ©seau(x) SADIE dÃ©tectÃ©(s): $sadieNetwork" -ForegroundColor Green
    
    # Inspecter chaque rÃ©seau SADIE trouvÃ©
    foreach ($network in $sadieNetwork) {
        $networkDetails = docker network inspect $network --format '{{.Name}} - {{.Driver}} - {{range .IPAM.Config}}{{.Subnet}}{{end}}'
        Write-Host "DÃ©tails du rÃ©seau $network : $networkDetails" -ForegroundColor White
        
        # VÃ©rifier les conteneurs connectÃ©s Ã  ce rÃ©seau
        $connectedContainers = docker network inspect $network --format '{{range .Containers}}{{.Name}} {{end}}'
        if ($connectedContainers) {
            Write-Host "Conteneurs connectÃ©s: $connectedContainers" -ForegroundColor White
        } else {
            Write-Host "Aucun conteneur connectÃ© Ã  ce rÃ©seau." -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "Aucun rÃ©seau SADIE dÃ©tectÃ©." -ForegroundColor Yellow
}

# Nettoyage des ressources de test
Write-Host "`nNettoyage des ressources de test..." -ForegroundColor Yellow
docker stop sadie-network-test1 sadie-network-test2 2>&1 | Out-Null
docker rm sadie-network-test1 sadie-network-test2 2>&1 | Out-Null
docker network rm $testNetworkName 2>&1 | Out-Null
Write-Host "âœ… Ressources de test nettoyÃ©es." -ForegroundColor Green

# Recommandations finales
Write-Host "`n=== RECOMMANDATIONS ===" -ForegroundColor Cyan
Write-Host "1. Assurez-vous que la MTU est rÃ©glÃ©e Ã  1500 pour de meilleures performances rÃ©seau" -ForegroundColor White
Write-Host "2. Si la latence est Ã©levÃ©e, essayez d'utiliser le driver 'host' pour les conteneurs nÃ©cessitant de hautes performances" -ForegroundColor White
Write-Host "3. Pour les communications entre conteneurs, utilisez toujours un rÃ©seau Docker dÃ©diÃ© plutÃ´t que le rÃ©seau 'bridge' par dÃ©faut" -ForegroundColor White
Write-Host "4. Optimisez les paramÃ¨tres DNS dans votre fichier docker-compose.yml:" -ForegroundColor White
Write-Host "   dns: [8.8.8.8, 8.8.4.4]" -ForegroundColor Gray
Write-Host "   dns_search: []" -ForegroundColor Gray

Write-Host "`nTest de performance rÃ©seau Docker terminÃ©!" -ForegroundColor Green 