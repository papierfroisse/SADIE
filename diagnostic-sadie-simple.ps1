!/usr/bin/env pwsh

# SADIE - Diagnostic simplifiÃ©
# ===========================

# Affichage du titre
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "       DIAGNOSTIC SADIE - RAPPORT SIMPLIFIÃ‰    " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Section 1: Informations sur le systÃ¨me
Write-Host "INFORMATIONS SYSTÃˆME" -ForegroundColor Yellow
Write-Host "------------------" -ForegroundColor Yellow
Write-Host "OS:" $(Get-CimInstance Win32_OperatingSystem).Caption -ForegroundColor White
Write-Host "PowerShell:" $PSVersionTable.PSVersion -ForegroundColor White
Write-Host "Date et heure:" (Get-Date) -ForegroundColor White
Write-Host ""

# Section 2: VÃ©rification de Docker
Write-Host "VÃ‰RIFICATION DOCKER" -ForegroundColor Yellow
Write-Host "------------------" -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "Docker installÃ©: $dockerVersion" -ForegroundColor Green
    
    Write-Host "`nConteneurs SADIE:" -ForegroundColor White
    docker ps -a | Select-String "sadie"
    
    Write-Host "`nÃ‰tat des conteneurs:" -ForegroundColor White
    docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | Select-String "sadie"
    
    Write-Host "`nUtilisation des ressources:" -ForegroundColor White
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    
} catch {
    Write-Host "Erreur lors de la vÃ©rification de Docker: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Section 3: VÃ©rification rÃ©seau
Write-Host "VÃ‰RIFICATION RÃ‰SEAU" -ForegroundColor Yellow
Write-Host "-----------------" -ForegroundColor Yellow
try {
    Write-Host "RÃ©seaux Docker:" -ForegroundColor White
    docker network ls
    
    Write-Host "`nVÃ©rification des ports:" -ForegroundColor White
    
    $frontendPort = 3000
    $backendPort = 8000
    
    $testFrontend = Test-NetConnection -ComputerName localhost -Port $frontendPort -WarningAction SilentlyContinue -InformationLevel Quiet
    if ($testFrontend) {
        Write-Host "Port $frontendPort (frontend): " -NoNewline
        Write-Host "OUVERT" -ForegroundColor Green
    } else {
        Write-Host "Port $frontendPort (frontend): " -NoNewline
        Write-Host "FERMÃ‰" -ForegroundColor Red
    }
    
    $testBackend = Test-NetConnection -ComputerName localhost -Port $backendPort -WarningAction SilentlyContinue -InformationLevel Quiet
    if ($testBackend) {
        Write-Host "Port $backendPort (backend): " -NoNewline
        Write-Host "OUVERT" -ForegroundColor Green
    } else {
        Write-Host "Port $backendPort (backend): " -NoNewline
        Write-Host "FERMÃ‰" -ForegroundColor Red
    }
} catch {
    Write-Host "Erreur lors de la vÃ©rification rÃ©seau: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Section 4: Logs des conteneurs
Write-Host "LOGS DES CONTENEURS" -ForegroundColor Yellow
Write-Host "-----------------" -ForegroundColor Yellow
try {
    Write-Host "Derniers logs du frontend (10 lignes):" -ForegroundColor White
    docker logs sadie-frontend --tail 10
    
    Write-Host "`nDerniers logs du backend (10 lignes):" -ForegroundColor White
    docker logs sadie-backend --tail 10 2>$null
} catch {
    Write-Host "Erreur lors de la rÃ©cupÃ©ration des logs: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Section 5: Recommandations
Write-Host "RECOMMANDATIONS" -ForegroundColor Yellow
Write-Host "--------------" -ForegroundColor Yellow

# VÃ©rifier l'espace disque
$diskInfo = Get-PSDrive C | Select-Object Used, Free
$freeGB = [math]::Round($diskInfo.Free / 1GB, 2)
$usedGB = [math]::Round($diskInfo.Used / 1GB, 2)
$percentUsed = [math]::Round(($diskInfo.Used / ($diskInfo.Used + $diskInfo.Free)) * 100, 2)

Write-Host "Espace disque: $usedGB GB utilisÃ©s / $freeGB GB libres ($percentUsed% utilisÃ©)" -ForegroundColor White

if ($percentUsed -gt 90) {
    Write-Host "âš ï¸ Espace disque critique! LibÃ©rez de l'espace." -ForegroundColor Red
} elseif ($percentUsed -gt 80) {
    Write-Host "âš ï¸ Espace disque faible. Envisagez de nettoyer le disque." -ForegroundColor Yellow
} else {
    Write-Host "âœ… Espace disque suffisant." -ForegroundColor Green
}

# Conclusion
Write-Host "`nDIAGNOSTIC TERMINÃ‰" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan 