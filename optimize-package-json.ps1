!/usr/bin/env pwsh

Write-Host "Optimisation du fichier package.json pour SADIE Frontend..." -ForegroundColor Cyan

# Chemin vers le fichier package.json
$packageJsonPath = "sadie/web/static/package.json"

# VÃ©rifier si le fichier existe
if (-not (Test-Path $packageJsonPath)) {
    Write-Host "Erreur: Le fichier package.json n'a pas Ã©tÃ© trouvÃ© Ã  l'emplacement: $packageJsonPath" -ForegroundColor Red
    exit 1
}

# Faire une sauvegarde du fichier original
$backupPath = "$packageJsonPath.bak"
Copy-Item $packageJsonPath $backupPath
Write-Host "Sauvegarde crÃ©Ã©e: $backupPath" -ForegroundColor Green

# Charger le fichier package.json
try {
    $packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
    Write-Host "Package.json chargÃ© avec succÃ¨s." -ForegroundColor Green
} catch {
    Write-Host "Erreur lors du chargement du fichier package.json: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`nOptimisations en cours..." -ForegroundColor Yellow

# Ajouter un script start:safe pour le dÃ©marrage Docker avec limite de mÃ©moire
if (-not ($packageJson.scripts.PSObject.Properties.Name -contains "start:safe")) {
    $packageJson.scripts | Add-Member -Name "start:safe" -Value "cross-env NODE_OPTIONS=--max-old-space-size=4096 GENERATE_SOURCEMAP=false react-scripts start" -MemberType NoteProperty
    Write-Host "âœ… Ajout du script start:safe avec optimisation mÃ©moire" -ForegroundColor Green
}

# Ajouter un script de dÃ©marrage rapide
if (-not ($packageJson.scripts.PSObject.Properties.Name -contains "start:fast")) {
    $packageJson.scripts | Add-Member -Name "start:fast" -Value "cross-env NODE_ENV=development BROWSER=none FAST_REFRESH=true react-scripts start" -MemberType NoteProperty
    Write-Host "âœ… Ajout du script start:fast pour dÃ©veloppement accÃ©lÃ©rÃ©" -ForegroundColor Green
}

# Ajouter script pour analyse des performances
if (-not ($packageJson.scripts.PSObject.Properties.Name -contains "analyze:bundle")) {
    $packageJson.scripts | Add-Member -Name "analyze:bundle" -Value "source-map-explorer 'build/static/js/*.js' --html analyze-report.html" -MemberType NoteProperty
    Write-Host "âœ… Ajout du script analyze:bundle pour analyser les performances" -ForegroundColor Green
}

# Ajouter un script pour nettoyer le cache
if (-not ($packageJson.scripts.PSObject.Properties.Name -contains "clean")) {
    $packageJson.scripts | Add-Member -Name "clean" -Value "rimraf build node_modules/.cache" -MemberType NoteProperty
    Write-Host "âœ… Ajout du script clean pour nettoyer le cache" -ForegroundColor Green
}

# Optimiser browserslist pour meilleure compatibilitÃ©
$packageJson.browserslist.production = @(">0.5%", "not dead", "not IE 11", "not op_mini all")
Write-Host "âœ… Optimisation du browserslist pour de meilleures performances" -ForegroundColor Green

# Ajouter des configurations pour optimiser le build
if (-not ($packageJson.PSObject.Properties.Name -contains "resolutions")) {
    $packageJson | Add-Member -Name "resolutions" -Value (@{
        "browserslist" = "^4.22.1"
        "eslint-plugin-react" = "^7.33.2"
        "react" = "^18.2.0"
        "react-dom" = "^18.2.0"
    }) -MemberType NoteProperty
    Write-Host "âœ… Ajout des rÃ©solutions pour Ã©viter les conflits de dÃ©pendances" -ForegroundColor Green
}

# Ajouter configurations pour jest
$packageJson.jest.coveragePathIgnorePatterns = @(
    "/node_modules/",
    "/tests/mocks/"
)
$packageJson.jest.collectCoverageFrom = @(
    "src/**/*.{js,jsx,ts,tsx}",
    "!src/**/*.d.ts",
    "!src/index.tsx",
    "!src/serviceWorker.ts"
)
Write-Host "âœ… AmÃ©lioration de la configuration de tests" -ForegroundColor Green

# Sauvegarder les modifications
try {
    $packageJson | ConvertTo-Json -Depth 10 | Set-Content $packageJsonPath
    Write-Host "`nLe fichier package.json a Ã©tÃ© optimisÃ© avec succÃ¨s!" -ForegroundColor Green
} catch {
    Write-Host "Erreur lors de la sauvegarde des modifications: $_" -ForegroundColor Red
    exit 1
}

# Installer rimraf s'il est requis pour le script clean
Write-Host "`nInstallation des dÃ©pendances requises pour les nouveaux scripts..." -ForegroundColor Yellow
try {
    $currentDir = Get-Location
    Set-Location (Split-Path -Parent $packageJsonPath)
    
    # VÃ©rifier si rimraf est installÃ©
    npm list rimraf --depth=0 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installation de rimraf..." -ForegroundColor Yellow
        npm install rimraf --save-dev
    } else {
        Write-Host "rimraf est dÃ©jÃ  installÃ©." -ForegroundColor Green
    }
    
    # VÃ©rifier si cross-env est installÃ©
    npm list cross-env --depth=0 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installation de cross-env..." -ForegroundColor Yellow
        npm install cross-env --save-dev
    } else {
        Write-Host "cross-env est dÃ©jÃ  installÃ©." -ForegroundColor Green
    }
    
    Set-Location $currentDir
} catch {
    Write-Host "Erreur lors de l'installation des dÃ©pendances: $_" -ForegroundColor Red
    Set-Location $currentDir
}

Write-Host "`nOptimisation package.json terminÃ©e!" -ForegroundColor Cyan
Write-Host "Recommandation: ExÃ©cutez 'cd sadie/web/static && npm install' pour mettre Ã  jour node_modules avec les nouvelles dÃ©pendances." -ForegroundColor Yellow 