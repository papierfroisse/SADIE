!/usr/bin/env pwsh

# Script pour corriger l'encodage des fichiers PowerShell
# Ce script convertit tous les fichiers .ps1 en UTF-8 avec BOM

# ParamÃ¨tres
param(
    [switch]$Force = $false,
    [string]$Directory = ".",
    [switch]$Recursive = $true,
    [switch]$WhatIf = $false
)

# BanniÃ¨re
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  CORRECTION D'ENCODAGE DES SCRIPTS PS1  " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Trouver tous les fichiers .ps1
$searchPattern = "*.ps1"
$searchOption = if ($Recursive) { "AllDirectories" } else { "TopDirectoryOnly" }
$files = Get-ChildItem -Path $Directory -Filter $searchPattern -Recurse:$Recursive

Write-Host "Fichiers PowerShell trouvÃ©s: $($files.Count)" -ForegroundColor Yellow
Write-Host ""

$convertedCount = 0
$skippedCount = 0
$errorCount = 0

foreach ($file in $files) {
    Write-Host "Traitement de $($file.FullName)..." -NoNewline
    
    try {
        # Lire le contenu du fichier
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        
        if ($content -ne $null) {
            # Supprimer le BOM existant s'il y en a un
            if ($content.StartsWith([char]0xFEFF)) {
                $content = $content.Substring(1)
            }
            
            # VÃ©rifier si le fichier contient des caractÃ¨res accentuÃ©s ou non-ASCII
            $containsAccents = $content -match "[^\x00-\x7F]"
            
            if ($containsAccents -or $Force) {
                # CrÃ©er une sauvegarde
                $backupPath = "$($file.FullName).bak"
                Copy-Item -Path $file.FullName -Destination $backupPath -Force
                
                if (-not $WhatIf) {
                    # RÃ©Ã©crire le fichier en UTF-8 avec BOM
                    $Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $true
                    [System.IO.File]::WriteAllText($file.FullName, $content, $Utf8NoBomEncoding)
                    
                    Write-Host " [CONVERTI]" -ForegroundColor Green
                    $convertedCount++
                } else {
                    Write-Host " [SERAIT CONVERTI]" -ForegroundColor Green
                    $convertedCount++
                }
            } else {
                Write-Host " [IGNORE - Pas de caractÃ¨res spÃ©ciaux]" -ForegroundColor Gray
                $skippedCount++
            }
        } else {
            Write-Host " [IGNORE - Fichier vide]" -ForegroundColor Gray
            $skippedCount++
        }
    } catch {
        Write-Host " [ERREUR - $($_.Exception.Message)]" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Host "RÃ©sumÃ©:" -ForegroundColor Cyan
Write-Host "- Fichiers traitÃ©s: $($files.Count)" -ForegroundColor White
Write-Host "- Fichiers convertis: $convertedCount" -ForegroundColor Green
Write-Host "- Fichiers ignorÃ©s: $skippedCount" -ForegroundColor Gray
Write-Host "- Erreurs: $errorCount" -ForegroundColor Red
Write-Host ""

if (-not $WhatIf) {
    Write-Host "Conversion terminÃ©e. Les fichiers ont Ã©tÃ© convertis en UTF-8 avec BOM." -ForegroundColor Green
} else {
    Write-Host "Simulation terminÃ©e. Aucun fichier n'a Ã©tÃ© modifiÃ©." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Pour appliquer rÃ©ellement les changements, exÃ©cutez sans l'option -WhatIf" -ForegroundColor Yellow
Write-Host "" 