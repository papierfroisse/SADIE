!/usr/bin/env pwsh

# SADIE - Installateur des outils d'optimisation
# ==============================================

# ParamÃ¨tres
param(
    [switch]$Force = $false,
    [string]$TargetDir = ".",
    [switch]$SkipPrerequisites = $false
)

# Configuration
$toolsVersion = "1.0.0"
$requiredPowerShellVersion = "5.1"
$requiredTools = @("docker", "docker-compose", "node")
$scripts = @(
    "sadie-optimize.ps1",
    "optimize-dockerfile.ps1",
    "optimize-package-json.ps1",
    "optimize-network.ps1",
    "restart-containers.ps1",
    "restart-sadie.ps1",
    "diagnostic-complet.ps1",
    "README-SADIE-TOOLS.md"
)

# Fonction pour afficher une banniÃ¨re
function Show-Banner {
    Clear-Host
    Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
    Write-Host "â•‘                                                              â•‘" -ForegroundColor Cyan
    Write-Host "â•‘         INSTALLATION DES OUTILS D'OPTIMISATION SADIE         â•‘" -ForegroundColor Cyan
    Write-Host "â•‘                    Version $toolsVersion                     â•‘" -ForegroundColor Cyan
    Write-Host "â•‘                                                              â•‘" -ForegroundColor Cyan
    Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
    Write-Host ""
}

# Fonction pour vÃ©rifier les prÃ©requis
function Check-Prerequisites {
    Write-Host "VÃ©rification des prÃ©requis..." -ForegroundColor Yellow
    
    # VÃ©rifier la version de PowerShell
    $psVersion = $PSVersionTable.PSVersion.Major
    if ($psVersion -lt $requiredPowerShellVersion) {
        Write-Host "âŒ PowerShell version $psVersion dÃ©tectÃ©e. Version $requiredPowerShellVersion ou supÃ©rieure requise." -ForegroundColor Red
        Write-Host "Veuillez mettre Ã  jour PowerShell: https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell" -ForegroundColor Red
        if (-not $Force) {
            exit 1
        }
    } else {
        Write-Host "âœ… PowerShell version $psVersion dÃ©tectÃ©e." -ForegroundColor Green
    }
    
    # VÃ©rifier les outils requis
    foreach ($tool in $requiredTools) {
        $toolExists = $null
        
        try {
            $toolExists = Get-Command $tool -ErrorAction SilentlyContinue
        } catch {
            $toolExists = $null
        }
        
        if ($null -eq $toolExists) {
            Write-Host "âŒ $tool non trouvÃ©. Veuillez l'installer avant de continuer." -ForegroundColor Red
            
            switch ($tool) {
                "docker" {
                    Write-Host "   Pour installer Docker: https://docs.docker.com/get-docker/" -ForegroundColor Red
                }
                "docker-compose" {
                    Write-Host "   Docker Compose est gÃ©nÃ©ralement inclus avec Docker Desktop" -ForegroundColor Red
                }
                "node" {
                    Write-Host "   Pour installer Node.js: https://nodejs.org/" -ForegroundColor Red
                }
            }
            
            if (-not $Force) {
                $continue = Read-Host "Voulez-vous continuer quand mÃªme? (O/N)"
                if ($continue -ne "O" -and $continue -ne "o") {
                    exit 1
                }
            }
        } else {
            Write-Host "âœ… $tool trouvÃ©." -ForegroundColor Green
        }
    }
    
    Write-Host "VÃ©rification des prÃ©requis terminÃ©e." -ForegroundColor Green
    Write-Host ""
}

# Fonction pour crÃ©er le rÃ©pertoire cible
function Create-TargetDirectory {
    if ($TargetDir -ne ".") {
        if (-not (Test-Path $TargetDir)) {
            Write-Host "CrÃ©ation du rÃ©pertoire cible $TargetDir..." -ForegroundColor Yellow
            New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
        }
        
        # Se dÃ©placer dans le rÃ©pertoire cible
        Set-Location $TargetDir
        Write-Host "RÃ©pertoire de travail actuel: $(Get-Location)" -ForegroundColor Green
        Write-Host ""
    }
}

# Fonction pour installer les scripts
function Install-Scripts {
    Write-Host "Installation des scripts d'optimisation SADIE..." -ForegroundColor Yellow
    
    # VÃ©rification prÃ©alable des scripts existants
    $existingScripts = @()
    foreach ($script in $scripts) {
        if (Test-Path $script) {
            $existingScripts += $script
        }
    }
    
    # Demander confirmation si des scripts existent dÃ©jÃ 
    if ($existingScripts.Count -gt 0 -and -not $Force) {
        Write-Host "Les scripts suivants existent dÃ©jÃ :" -ForegroundColor Yellow
        foreach ($script in $existingScripts) {
            Write-Host "- $script" -ForegroundColor Yellow
        }
        
        $overwrite = Read-Host "Voulez-vous les Ã©craser? (O/N)"
        if ($overwrite -ne "O" -and $overwrite -ne "o") {
            Write-Host "Installation annulÃ©e." -ForegroundColor Red
            exit 1
        }
    }
    
    # Sauvegarde des scripts existants
    if ($existingScripts.Count -gt 0) {
        $backupDir = "sadie-tools-backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        
        Write-Host "Sauvegarde des scripts existants dans $backupDir..." -ForegroundColor Yellow
        foreach ($script in $existingScripts) {
            Copy-Item $script -Destination $backupDir
        }
        Write-Host "Sauvegarde terminÃ©e." -ForegroundColor Green
    }
    
    # TÃ©lÃ©chargement ou copie des scripts depuis le rÃ©pertoire actuel
    $sourceDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
    
    foreach ($script in $scripts) {
        $sourcePath = Join-Path -Path $sourceDir -ChildPath $script
        
        if (Test-Path $sourcePath) {
            Write-Host "Copie de $script..." -ForegroundColor Yellow
            Copy-Item -Path $sourcePath -Destination .\ -Force
        } else {
            Write-Host "âš ï¸ Le script $script n'a pas Ã©tÃ© trouvÃ© dans le rÃ©pertoire source." -ForegroundColor Yellow
            Write-Host "CrÃ©ation d'un fichier temporaire..." -ForegroundColor Yellow
            
            # CrÃ©ation d'un fichier temporaire avec un message d'erreur
            $errorContent = @"
# Ce fichier a Ã©tÃ© crÃ©Ã© par l'installateur SADIE Tools
# Le script original n'a pas Ã©tÃ© trouvÃ©.
# Veuillez tÃ©lÃ©charger manuellement tous les scripts depuis le dÃ©pÃ´t officiel.

Write-Host "Erreur: Ce script est un placeholder. Veuillez tÃ©lÃ©charger la version complÃ¨te." -ForegroundColor Red
"@
            Set-Content -Path $script -Value $errorContent -Force
        }
    }
    
    Write-Host "Installation des scripts terminÃ©e." -ForegroundColor Green
    Write-Host ""
}

# Fonction pour configurer les permissions
function Set-ScriptPermissions {
    Write-Host "Configuration des permissions d'exÃ©cution..." -ForegroundColor Yellow
    
    try {
        $currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
        if ($currentPolicy -eq "Restricted" -or $currentPolicy -eq "AllSigned") {
            Write-Host "Modification de la politique d'exÃ©cution PowerShell pour l'utilisateur actuel..." -ForegroundColor Yellow
            Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
            Write-Host "Politique d'exÃ©cution dÃ©finie sur RemoteSigned pour l'utilisateur actuel." -ForegroundColor Green
        } else {
            Write-Host "âœ… Politique d'exÃ©cution actuelle ($currentPolicy) compatible avec les scripts." -ForegroundColor Green
        }
    } catch {
        Write-Host "âš ï¸ Impossible de modifier la politique d'exÃ©cution. Vous devrez peut-Ãªtre exÃ©cuter cette commande manuellement:" -ForegroundColor Yellow
        Write-Host "Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned" -ForegroundColor Yellow
    }
    
    Write-Host "Configuration des permissions terminÃ©e." -ForegroundColor Green
    Write-Host ""
}

# Fonction d'instructions finales
function Show-FinalInstructions {
    Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Green
    Write-Host "â•‘                                                              â•‘" -ForegroundColor Green
    Write-Host "â•‘              INSTALLATION TERMINÃ‰E AVEC SUCCÃˆS               â•‘" -ForegroundColor Green
    Write-Host "â•‘                                                              â•‘" -ForegroundColor Green
    Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
    Write-Host ""
    Write-Host "Pour dÃ©marrer la suite d'outils d'optimisation SADIE, exÃ©cutez:" -ForegroundColor White
    Write-Host "  ./sadie-optimize.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Pour en savoir plus sur les outils disponibles, consultez:" -ForegroundColor White
    Write-Host "  README-SADIE-TOOLS.md" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Si vous rencontrez des problÃ¨mes, exÃ©cutez le diagnostic complet:" -ForegroundColor White
    Write-Host "  ./diagnostic-complet.ps1" -ForegroundColor Cyan
    Write-Host ""
}

# Programme principal
Show-Banner

if (-not $SkipPrerequisites) {
    Check-Prerequisites
}

Create-TargetDirectory
Install-Scripts
Set-ScriptPermissions
Show-FinalInstructions 