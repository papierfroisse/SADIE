!/usr/bin/env pwsh

# Optimisation complÃ¨te du systÃ¨me SADIE

Write-Host "
===================================================
    OPTIMISATION COMPLÃˆTE DU SYSTÃˆME SADIE
===================================================
" -ForegroundColor Cyan

# Fonction pour afficher le titre d'une Ã©tape
function Show-StepTitle {
    param (
        [string]$title,
        [int]$stepNumber,
        [int]$totalSteps
    )
    
    Write-Host "`n[$stepNumber/$totalSteps] $title" -ForegroundColor Magenta
    Write-Host "---------------------------------------------------" -ForegroundColor Magenta
}

# Fonction pour exÃ©cuter un script et gÃ©rer les erreurs
function Invoke-OptimizationScript {
    param (
        [string]$scriptPath,
        [string]$description,
        [int]$stepNumber,
        [int]$totalSteps
    )
    
    Show-StepTitle -title $description -stepNumber $stepNumber -totalSteps $totalSteps
    
    if (Test-Path $scriptPath) {
        try {
            & $scriptPath
            if ($LASTEXITCODE -ne 0) {
                Write-Host "`nâŒ Le script '$scriptPath' s'est terminÃ© avec des erreurs (code: $LASTEXITCODE)" -ForegroundColor Red
                return $false
            }
            Write-Host "`nâœ… $description terminÃ© avec succÃ¨s" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "`nâŒ Erreur lors de l'exÃ©cution de '$scriptPath': $_" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "`nâŒ Script '$scriptPath' introuvable" -ForegroundColor Red
        return $false
    }
}

# Fonction pour demander la confirmation de l'utilisateur
function Confirm-Execution {
    param (
        [string]$message
    )
    
    Write-Host "`n$message" -ForegroundColor Yellow
    $confirmation = Read-Host "Voulez-vous continuer? (O/N)"
    
    return ($confirmation -eq "O" -or $confirmation -eq "o")
}

# Variables pour suivre les progrÃ¨s
$totalSteps = 5
$completedSteps = 0
$failedSteps = 0

# CrÃ©ation d'un dossier pour les logs
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFolder = "sadie_optimization_logs_$timestamp"
if (-not (Test-Path $logFolder)) {
    New-Item -ItemType Directory -Path $logFolder | Out-Null
}

Write-Host "Les logs d'optimisation seront enregistrÃ©s dans : $logFolder" -ForegroundColor Yellow

# DÃ©marrer la journalisation
Start-Transcript -Path "$logFolder/optimisation_complete.log" -Append

Write-Host "`nDate de dÃ©but: $(Get-Date)" -ForegroundColor White
Write-Host "VÃ©rification des scripts d'optimisation..." -ForegroundColor White

# VÃ©rifier si tous les scripts existent
$scriptsToRun = @(
    @{Path="./optimize-package-json.ps1"; Description="Optimisation du fichier package.json"},
    @{Path="./optimize-dockerfile.ps1"; Description="Optimisation du Dockerfile"},
    @{Path="./check-docker-network.ps1"; Description="VÃ©rification des performances du rÃ©seau Docker"},
    @{Path="./clean-docker.ps1"; Description="Nettoyage des ressources Docker inutilisÃ©es"},
    @{Path="./restart-sadie.ps1"; Description="RedÃ©marrage des conteneurs SADIE"}
)

$missingScripts = $scriptsToRun | Where-Object { -not (Test-Path $_.Path) }
if ($missingScripts.Count -gt 0) {
    Write-Host "`nATTENTION: Certains scripts sont manquants:" -ForegroundColor Red
    $missingScripts | ForEach-Object { Write-Host "- $($_.Path)" -ForegroundColor Red }
    
    if (-not (Confirm-Execution "Certains scripts sont manquants. L'optimisation pourrait Ãªtre incomplÃ¨te.")) {
        Write-Host "Optimisation annulÃ©e par l'utilisateur." -ForegroundColor Yellow
        Stop-Transcript
        exit 0
    }
}

Write-Host "`nINFORMATION: L'optimisation va procÃ©der en $totalSteps Ã©tapes:" -ForegroundColor Yellow
$scriptsToRun | ForEach-Object { Write-Host "- $($_.Description)" -ForegroundColor White }

if (-not (Confirm-Execution "Cela va optimiser l'ensemble du systÃ¨me SADIE. Assurez-vous d'avoir sauvegardÃ© vos donnÃ©es.")) {
    Write-Host "Optimisation annulÃ©e par l'utilisateur." -ForegroundColor Yellow
    Stop-Transcript
    exit 0
}

# ExÃ©cution des scripts d'optimisation
$stepNumber = 0
foreach ($script in $scriptsToRun) {
    $stepNumber++
    
    # Sauvegarde de la sortie du script
    $scriptLogFile = "$logFolder/$($script.Path -replace '[\.\/\\]', '_').log"
    Start-Transcript -Path $scriptLogFile
    
    $success = Invoke-OptimizationScript -scriptPath $script.Path -description $script.Description -stepNumber $stepNumber -totalSteps $totalSteps
    
    Stop-Transcript
    
    if ($success) {
        $completedSteps++
    } else {
        $failedSteps++
    }
    
    # Pause entre les scripts pour permettre Ã  l'utilisateur de lire les rÃ©sultats
    if ($stepNumber -lt $totalSteps) {
        Write-Host "`nPassage Ã  l'Ã©tape suivante dans 3 secondes..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
}

# Afficher un rÃ©sumÃ©
Write-Host "`n
===================================================
                RÃ‰SUMÃ‰ D'OPTIMISATION
===================================================
" -ForegroundColor Cyan

Write-Host "Date de fin: $(Get-Date)" -ForegroundColor White
Write-Host "Ã‰tapes rÃ©ussies: $completedSteps/$totalSteps" -ForegroundColor $(if ($completedSteps -eq $totalSteps) { "Green" } else { "Yellow" })

if ($failedSteps -gt 0) {
    Write-Host "Ã‰tapes Ã©chouÃ©es: $failedSteps/$totalSteps" -ForegroundColor Red
    Write-Host "`nConsultez les logs pour plus de dÃ©tails: $logFolder" -ForegroundColor Yellow
}

# Afficher des recommandations finales
Write-Host "`nRECOMMANDATIONS FINALES:" -ForegroundColor Green
Write-Host "1. VÃ©rifiez le fonctionnement de l'application aprÃ¨s optimisation" -ForegroundColor White
Write-Host "2. ExÃ©cutez des tests pour vous assurer que tout fonctionne comme prÃ©vu" -ForegroundColor White
Write-Host "3. Utilisez './diagnostic-sadie-simple.ps1' rÃ©guliÃ¨rement pour surveiller l'Ã©tat du systÃ¨me" -ForegroundColor White
Write-Host "4. Planifiez une optimisation complÃ¨te chaque mois pour maintenir les performances" -ForegroundColor White

Write-Host "`nOptimisation complÃ¨te du systÃ¨me SADIE terminÃ©e!" -ForegroundColor Cyan

# ArrÃªter la journalisation
Stop-Transcript 