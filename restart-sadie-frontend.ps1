rite-Host "RedÃ©marrage du conteneur SADIE Frontend..." -ForegroundColor Cyan

# 1. ArrÃªt et suppression du conteneur existant
Write-Host "1. ArrÃªt du conteneur..." -ForegroundColor Yellow
docker stop sadie-frontend

Write-Host "2. Suppression du conteneur..." -ForegroundColor Yellow
docker rm sadie-frontend

# 2. Modification du docker-compose.yml si nÃ©cessaire
Write-Host "3. VÃ©rification de la configuration..." -ForegroundColor Yellow
$composeExists = Test-Path "docker-compose.yml"
if ($composeExists) {
    $composeContent = Get-Content docker-compose.yml -Raw
    if (-not ($composeContent -match "NODE_OPTIONS")) {
        Write-Host "   Ajout de la configuration mÃ©moire..." -ForegroundColor Yellow
        $composeContent = $composeContent -replace '(services:\s+frontend:\s+)', "`$1`n      environment:`n        - NODE_OPTIONS=--max-old-space-size=4096`n"
        Set-Content docker-compose.yml $composeContent
        Write-Host "   Configuration mÃ©moire ajoutÃ©e au docker-compose.yml" -ForegroundColor Green
    }
}

# 3. Optimisation du package.json
Write-Host "4. VÃ©rification de package.json..." -ForegroundColor Yellow
$packageJsonPath = "sadie/web/static/package.json"
if (Test-Path $packageJsonPath) {
    # Sauvegarde du fichier original
    Copy-Item $packageJsonPath "$packageJsonPath.bak"
    Write-Host "   Sauvegarde crÃ©Ã©e: $packageJsonPath.bak" -ForegroundColor Green
    
    # Lecture et modification du fichier
    $packageJsonContent = Get-Content $packageJsonPath | ConvertFrom-Json
    
    # Ajout des scripts optimisÃ©s s'ils n'existent pas
    if (-not $packageJsonContent.scripts.'start:safe') {
        $packageJsonContent.scripts | Add-Member -Name "start:safe" -Value "cross-env NODE_OPTIONS=--max-old-space-size=4096 react-scripts start" -MemberType NoteProperty -Force
        Write-Host "   Script start:safe ajoutÃ©" -ForegroundColor Green
    }
    
    if (-not $packageJsonContent.scripts.'start:prod') {
        $packageJsonContent.scripts | Add-Member -Name "start:prod" -Value "cross-env GENERATE_SOURCEMAP=false react-scripts start" -MemberType NoteProperty -Force
        Write-Host "   Script start:prod ajoutÃ©" -ForegroundColor Green
    }
    
    # Sauvegarde des modifications
    $packageJsonContent | ConvertTo-Json -Depth 10 | Set-Content $packageJsonPath
    Write-Host "   package.json mis Ã  jour" -ForegroundColor Green
}

# 4. RedÃ©marrage du conteneur avec docker-compose
Write-Host "5. RedÃ©marrage du conteneur..." -ForegroundColor Yellow
if ($composeExists) {
    docker-compose up -d frontend
} else {
    Write-Host "   Erreur: docker-compose.yml non trouvÃ©!" -ForegroundColor Red
    Write-Host "   Veuillez exÃ©cuter la commande manuellement: docker run -d --name sadie-frontend -e NODE_OPTIONS=--max-old-space-size=4096 -p 3000:3000 sadie-frontend" -ForegroundColor Yellow
}

# 5. VÃ©rification du dÃ©marrage
Write-Host "6. VÃ©rification du dÃ©marrage (patientez)..." -ForegroundColor Yellow
Start-Sleep -Seconds 20
$logs = docker logs sadie-frontend --tail 20

if ($logs -match "Compiled successfully") {
    Write-Host "`nLe serveur frontend a dÃ©marrÃ© avec succÃ¨s!" -ForegroundColor Green
    Write-Host "Interface accessible Ã : http://localhost:3000" -ForegroundColor Cyan
} elseif ($logs -match "Starting the development server") {
    Write-Host "`nLe serveur frontend est en cours de dÃ©marrage..." -ForegroundColor Yellow
    Write-Host "VÃ©rifiez Ã  nouveau dans quelques instants avec: docker logs sadie-frontend" -ForegroundColor Cyan
} else {
    Write-Host "`nProblÃ¨me dÃ©tectÃ© lors du dÃ©marrage!" -ForegroundColor Red
    Write-Host "Consultez les logs pour plus de dÃ©tails: docker logs sadie-frontend" -ForegroundColor Yellow
} 